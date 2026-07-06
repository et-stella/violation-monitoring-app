import streamlit as st
import pandas as pd

st.set_page_config(page_title="커머셜 정책 위반 탐지기", page_icon="🛑", layout="wide")

st.title("🛑 커머셜 정책 위반 탐지기")
st.markdown("Sap Order ID 기준으로 구매수량 정책 위반 가능성을 탐지합니다.")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])

required_cols = ["sap order id", "purchase date", "return id", "article", "pcs"]

def clean_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

def detect_condition_1(df):
    """
    조건 1:
    365일 이내 동일 sap order id + 동일 article 구매수량 2개 초과
    """
    result = []

    for (sap_order_id, article), group in df.groupby(["sap order id", "article"]):
        group = group.sort_values("purchase date")
        last_date = group["purchase date"].max()

        window = group[
            (group["purchase date"] >= last_date - pd.Timedelta(days=365)) &
            (group["purchase date"] <= last_date)
        ]

        total_pcs = window["pcs"].sum()

        if total_pcs > 2:
            result.append({
                "Condition": "조건 1",
                "SAP Order ID": sap_order_id,
                "Article": article,
                "Total PCS": total_pcs,
                "Period": "365 Days"
            })

    return pd.DataFrame(result)


def detect_condition_2(df):
    """
    조건 2:
    365일 이내 동일 sap order id 당 구매수량 10개 초과
    """
    result = []

    for sap_order_id, group in df.groupby("sap order id"):
        group = group.sort_values("purchase date")
        last_date = group["purchase date"].max()

        window = group[
            (group["purchase date"] >= last_date - pd.Timedelta(days=365)) &
            (group["purchase date"] <= last_date)
        ]

        total_pcs = window["pcs"].sum()

        if total_pcs > 10:
            result.append({
                "Condition": "조건 2",
                "SAP Order ID": sap_order_id,
                "Article": "ALL",
                "Total PCS": total_pcs,
                "Period": "365 Days"
            })

    return pd.DataFrame(result)


def detect_condition_3(df):
    """
    조건 3:
    30일 이내 동일 sap order id 당 구매수량 5개 초과
    """
    result = []

    for sap_order_id, group in df.groupby("sap order id"):
        group = group.sort_values("purchase date")
        last_date = group["purchase date"].max()

        window = group[
            (group["purchase date"] >= last_date - pd.Timedelta(days=30)) &
            (group["purchase date"] <= last_date)
        ]

        total_pcs = window["pcs"].sum()

        if total_pcs > 5:
            result.append({
                "Condition": "조건 3",
                "SAP Order ID": sap_order_id,
                "Article": "ALL",
                "Total PCS": total_pcs,
                "Period": "30 Days"
            })

    return pd.DataFrame(result)


if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = clean_columns(df)

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❗ 필수 컬럼이 없습니다: {missing_cols}")
        st.stop()

    df["purchase date"] = pd.to_datetime(df["purchase date"], errors="coerce")
    df["pcs"] = pd.to_numeric(df["pcs"], errors="coerce").fillna(0)

    # 반품 row 제외: return id가 비어있는 구매건만 사용
    purchase_df = df[df["return id"].isna() | (df["return id"].astype(str).str.strip() == "")]

    st.subheader("✅ 업로드 데이터 미리보기")
    st.dataframe(df.head())

    result1 = detect_condition_1(purchase_df)
    result2 = detect_condition_2(purchase_df)
    result3 = detect_condition_3(purchase_df)

    total_result = pd.concat([result1, result2, result3], ignore_index=True)

    tab1, tab2, tab3, tab4 = st.tabs(["조건 1", "조건 2", "조건 3", "전체 결과"])

    with tab1:
        st.markdown("### 조건 1: 365일 이내 동일 Order ID + 동일 Article 2개 초과")
        st.write(f"위반 건수: {len(result1)}")
        st.dataframe(result1)

    with tab2:
        st.markdown("### 조건 2: 365일 이내 동일 Order ID 구매수량 10개 초과")
        st.write(f"위반 건수: {len(result2)}")
        st.dataframe(result2)

    with tab3:
        st.markdown("### 조건 3: 30일 이내 동일 Order ID 구매수량 5개 초과")
        st.write(f"위반 건수: {len(result3)}")
        st.dataframe(result3)

    with tab4:
        st.markdown("### 전체 위반 결과")
        st.write(f"총 위반 건수: {len(total_result)}")
        st.dataframe(total_result)

        csv = total_result.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 결과 다운로드 CSV",
            data=csv,
            file_name="commercial_policy_violation_result.csv",
            mime="text/csv"
        )

else:
    st.info("엑셀 파일을 업로드하세요.")
