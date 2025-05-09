import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="커머셜 정책 위반 탐지기", page_icon="🛑", layout="wide")
st.title("🛑 커머셜 정책 위반 탐지기")
st.markdown("고객의 구매 수량을 기반으로 정책 위반 가능성을 분석합니다.")

# 📁 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"], key="file_upload_1")

# 🧠 함수 정의 (NetQuantity 기준 + Article 기준 + NetQuantity 총합이 0인 그룹 제외)
def detect_condition_1(df):
    result = []
    for (sap, article), group in df.groupby(['SAPID', 'Article']):
        total_qty = group['NetQuantity'].sum()
        if total_qty <= 0:
            continue
        group = group.sort_values('PurchaseDate')
        for date in group['PurchaseDate']:
            qty = group[(group['PurchaseDate'] >= date - pd.Timedelta(days=365)) &
                        (group['PurchaseDate'] <= date)]['NetQuantity'].sum()
            if qty > 2:
                result.append({'SAPID': sap, 'Article': article, 'TotalQuantity': total_qty})
                break
    return pd.DataFrame(result)

def detect_condition_2(df):
    result = []
    for sap, group in df.groupby('SAPID'):
        group = group.sort_values('PurchaseDate')
        for date in group['PurchaseDate']:
            window = group[(group['PurchaseDate'] >= date - pd.Timedelta(days=30)) &
                           (group['PurchaseDate'] <= date)]
            qty_by_article = window.groupby('Article')['NetQuantity'].sum()
            qty_by_article = qty_by_article[qty_by_article > 0]
            if len(qty_by_article) > 5:
                for article, qty in qty_by_article.items():
                    result.append({'SAPID': sap, 'Article': article, 'TotalQuantity': qty})
                break
    return pd.DataFrame(result)

def detect_condition_3(df):
    result = []
    for sap, group in df.groupby('SAPID'):
        group = group.sort_values('PurchaseDate')
        for date in group['PurchaseDate']:
            window = group[(group['PurchaseDate'] >= date - pd.Timedelta(days=365)) &
                           (group['PurchaseDate'] <= date)]
            qty_by_article = window.groupby('Article')['NetQuantity'].sum()
            qty_by_article = qty_by_article[qty_by_article > 0]
            if len(qty_by_article) > 10:
                for article, qty in qty_by_article.items():
                    result.append({'SAPID': sap, 'Article': article, 'TotalQuantity': qty})
                break
    return pd.DataFrame(result)

def detect_heavy_returners(df):
    return_df = df[df['NetQuantity'] < 0]
    return_summary = return_df.groupby(['SAPID', 'Article'])['NetQuantity'].sum().reset_index()
    return_summary['ReturnQty'] = return_summary['NetQuantity'].abs()
    total_purchase = df[df['NetQuantity'] > 0].groupby(['SAPID', 'Article'])['NetQuantity'].sum().reset_index()
    merged = pd.merge(return_summary, total_purchase, on=['SAPID', 'Article'], how='left', suffixes=('_Return', '_Purchase'))
    merged['ReturnRate'] = merged['ReturnQty'] / merged['NetQuantity_Purchase']
    merged = merged.drop(columns=['NetQuantity_Return', 'NetQuantity_Purchase'])
    merged = merged[merged['ReturnRate'].notna()].sort_values(by='ReturnQty', ascending=False)
    return merged

# ✅ 실행 로직
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')
    df['NetQuantity'] = pd.to_numeric(df['NetQuantity'], errors='coerce').fillna(0)

    # 필수 컬럼 체크
    required_cols = ['SAPID', 'Article', 'PurchaseDate', 'NetQuantity']
    if not all(col in df.columns for col in required_cols):
        st.error(f"❗ 필수 컬럼이 없습니다: {required_cols}")
        st.stop()

    st.subheader("✅ 업로드한 데이터 미리보기")
    st.dataframe(df.head())

    # 조건별 탐지 실행 및 정렬 (안전하게 컬럼 체크 후 정렬)
    result1 = detect_condition_1(df)
    if 'TotalQuantity' in result1.columns:
        result1 = result1.sort_values(by='TotalQuantity', ascending=False)

    result2 = detect_condition_2(df)
    if 'TotalQuantity' in result2.columns:
        result2 = result2.sort_values(by='TotalQuantity', ascending=False)

    result3 = detect_condition_3(df)
    if 'TotalQuantity' in result3.columns:
        result3 = result3.sort_values(by='TotalQuantity', ascending=False)

    returners = detect_heavy_returners(df)

    # 결과 출력
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 조건 1", "🔍 조건 2", "🔍 조건 3", "↩️ 리턴 고객"])

    with tab1:
        st.markdown("**조건 1:** 동일 Article을 365일 내 수량 기준 3개 초과 구매")
        st.write(f"위반 고객 수: {result1['SAPID'].nunique()}명")
        st.dataframe(result1)

    with tab2:
        st.markdown("**조건 2:** 30일 내 서로 다른 Article을 수량 기준 5개 초과 구매")
        st.write(f"위반 고객 수: {result2['SAPID'].nunique()}명")
        st.dataframe(result2)

    with tab3:
        st.markdown("**조건 3:** 365일 내 서로 다른 Article을 수량 기준 10개 초과 구매")
        st.write(f"위반 고객 수: {result3['SAPID'].nunique()}명")
        st.dataframe(result3)

    with tab4:
        st.markdown("**리턴이 많은 고객 + Article별 리턴율**")
        st.write(f"리턴 고객 수: {returners['SAPID'].nunique()}명")
        st.dataframe(returners)

        # 리턴 수량 상위 10개 Article 시각화
        top_articles = returners.groupby('Article')['ReturnQty'].sum().sort_values(ascending=False).head(10)
        st.markdown("**📊 가장 많이 리턴된 Article Top 10**")
        fig, ax = plt.subplots()
        top_articles.plot(kind='bar', ax=ax)
        ax.set_ylabel("Return Quantity")
        ax.set_xlabel("Article")
        ax.set_title("Top 10 Returned Articles")
        st.pyplot(fig)

else:
    st.info("👈 왼쪽에서 엑셀 파일을 업로드하세요.")
