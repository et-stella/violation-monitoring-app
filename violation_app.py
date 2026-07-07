import streamlit as st
import pandas as pd
st.set_page_config(
   page_title="Commercial Policy Violation Monitor",
   page_icon="🛑",
   layout="wide"
)
st.title("🛑 Commercial Policy Violation Monitor")
st.caption("Customer ID 기준 구매수량 정책 위반 탐지")
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])
REQUIRED_COLS = ["Sap Order ID", "Purchase Date", "Return ID", "Article", "PCS"]

def prepare_data(df):
   missing = [c for c in REQUIRED_COLS if c not in df.columns]
   if missing:
       st.error(f"필수 컬럼이 없습니다: {missing}")
       st.stop()
   df = df.copy()
   df["Customer ID"] = df["Sap Order ID"].astype(str)
   df["Purchase Date"] = pd.to_datetime(df["Purchase Date"], errors="coerce")
   df["PCS"] = pd.to_numeric(df["PCS"], errors="coerce").fillna(0)
   df = df.dropna(subset=["Purchase Date"])
   df["Is Return"] = (
       df["Return ID"].notna()
& (df["Return ID"].astype(str).str.strip() != "")
   )
   df["Adjusted PCS"] = df["PCS"]
   df.loc[df["Is Return"], "Adjusted PCS"] = df.loc[df["Is Return"], "PCS"].abs() * -1
   return df

def detect_violation(df, group_cols, days, threshold, condition_name, article_level=False):
   results = []
   for keys, group in df.groupby(group_cols):
       group = group.sort_values("Purchase Date")
       for _, row in group.iterrows():
           end_date = row["Purchase Date"]
           start_date = end_date - pd.Timedelta(days=days)
           window = group[
               (group["Purchase Date"] >= start_date)
& (group["Purchase Date"] <= end_date)
           ]
           net_pcs = window["Adjusted PCS"].sum()
           if net_pcs > threshold:
               if article_level:
                   customer_id, article = keys
               else:
                   customer_id = keys
                   article = "ALL"
               results.append({
                   "Condition": condition_name,
                   "Customer ID": customer_id,
                   "Article": article,
                   "Period": f"{days} Days",
                   "Threshold": f"> {threshold}",
                   "Purchase Qty": window.loc[~window["Is Return"], "PCS"].sum(),
                   "Return Qty": window.loc[window["Is Return"], "Adjusted PCS"].sum(),
                   "Net PCS": net_pcs,
                   "Start Date": window["Purchase Date"].min(),
                   "End Date": window["Purchase Date"].max(),
                   "Result": "🔴 Violation"
               })
               break
   return pd.DataFrame(results)

if uploaded_file:
   raw_df = pd.read_excel(uploaded_file)
   df = prepare_data(raw_df)
   result1 = detect_violation(
       df=df,
       group_cols=["Customer ID", "Article"],
       days=365,
       threshold=2,
       condition_name="조건 1: 동일 Article 2개 초과",
       article_level=True
   )
   result2 = detect_violation(
       df=df,
       group_cols=["Customer ID"],
       days=365,
       threshold=10,
       condition_name="조건 2: 365일 10개 초과",
       article_level=False
   )
   result3 = detect_violation(
       df=df,
       group_cols=["Customer ID"],
       days=30,
       threshold=5,
       condition_name="조건 3: 30일 5개 초과",
       article_level=False
   )
   total_result = pd.concat([result1, result2, result3], ignore_index=True)
   st.subheader("📌 Summary")
   c1, c2, c3, c4 = st.columns(4)
   c1.metric("Total Rows", len(df))
   c2.metric("Condition 1", len(result1))
   c3.metric("Condition 2", len(result2))
   c4.metric("Condition 3", len(result3))
   tab1, tab2, tab3, tab4, tab5 = st.tabs([
       "조건 1",
       "조건 2",
       "조건 3",
       "전체 결과",
       "반품 확인"
   ])
   with tab1:
       st.markdown("### 조건 1: 365일 이내 동일 고객 + 동일 Article Net PCS > 2")
       if result1.empty:
           st.success("위반 건이 없습니다.")
       else:
           st.dataframe(result1, use_container_width=True)
   with tab2:
       st.markdown("### 조건 2: 365일 이내 동일 고객 Net PCS > 10")
       if result2.empty:
           st.success("위반 건이 없습니다.")
       else:
           st.dataframe(result2, use_container_width=True)
   with tab3:
       st.markdown("### 조건 3: 30일 이내 동일 고객 Net PCS > 5")
       if result3.empty:
           st.success("위반 건이 없습니다.")
       else:
           st.dataframe(result3, use_container_width=True)
   with tab4:
       st.markdown("### 전체 위반 결과")
       if total_result.empty:
           st.success("전체 위반 건이 없습니다.")
       else:
           st.dataframe(total_result, use_container_width=True)
           csv = total_result.to_csv(index=False).encode("utf-8-sig")
           st.download_button(
               "📥 CSV 다운로드",
               csv,
               "commercial_policy_violation_result.csv",
               "text/csv"
           )
   with tab5:
       st.markdown("### 반품 데이터 확인")
       return_df = df[df["Is Return"]].copy()
       if return_df.empty:
st.info("반품 데이터가 없습니다.")
       else:
           st.dataframe(
               return_df[
                   [
                       "Customer ID",
                       "Purchase Date",
                       "Return ID",
                       "Article",
                       "PCS",
                       "Adjusted PCS"
                   ]
               ],
               use_container_width=True
           )
   with st.expander("업로드 데이터 미리보기"):
       st.dataframe(df.head(100), use_container_width=True)
else:
st.info("엑셀 파일을 업로드하세요.")
