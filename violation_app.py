import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="커머셜 정책 위반 탐지기", page_icon="🛑", layout="wide")
st.title("🛑 커머셜 정책 위반 탐지기")
st.markdown("고객의 구매 수량을 기반으로 정책 위반 가능성을 분석합니다.")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"], key="file_upload_1")

# ✅ 조건 1: 동일 Article, 마지막 구매일 기준 365일 내 수량 > 2
def detect_condition_1(df):
    result = []
    for (sap, article), group in df.groupby(['SAPID', 'Article']):
        group = group.sort_values('PurchaseDate')
        last_date = group['PurchaseDate'].max()
        window = group[(group['PurchaseDate'] >= last_date - pd.Timedelta(days=365)) &
                       (group['PurchaseDate'] <= last_date)]
        qty = window['NetQuantity'].sum()
        if qty > 2:
            result.append({'SAPID': sap, 'Article': article, 'TotalQuantity': qty})
    return pd.DataFrame(result)

# ✅ 조건 2: 서로 다른 Article 5개 초과 (마지막 구매일 기준 30일)
def detect_condition_2(df):
    result = []
    for sap, group in df.groupby('SAPID'):
        group = group.sort_values('PurchaseDate')
        last_date = group['PurchaseDate'].max()
        window = group[(group['PurchaseDate'] >= last_date - pd.Timedelta(days=30)) &
                       (group['PurchaseDate'] <= last_date)]
        article_counts = window.groupby('Article')['NetQuantity'].sum()
        valid_articles = article_counts[article_counts != 0]
        if valid_articles.count() > 5:
            for article, qty in valid_articles.items():
                result.append({'SAPID': sap, 'Article': article, 'TotalQuantity': qty})
    return pd.DataFrame(result)

# ✅ 조건 3: 서로 다른 Article 10개 초과 (마지막 구매일 기준 365일)
def detect_condition_3(df):
    result = []
    for sap, group in df.groupby('SAPID'):
        group = group.sort_values('PurchaseDate')
        last_date = group['PurchaseDate'].max()
        window = group[(group['PurchaseDate'] >= last_date - pd.Timedelta(days=365)) &
                       (group['PurchaseDate'] <= last_date)]
        article_counts = window.groupby('Article')['NetQuantity'].sum()
        valid_articles = article_counts[article_counts != 0]
        if valid_articles.count() > 10:
            for article, qty in valid_articles.items():
                result.append({'SAPID': sap, 'Article': article, 'TotalQuantity': qty})
    return pd.DataFrame(result)

# ✅ 리턴 고객 분석
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

# ✅ 실행
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')
    df['NetQuantity'] = pd.to_numeric(df['NetQuantity'], errors='coerce').fillna(0)

    required_cols = ['SAPID', 'Article', 'PurchaseDate', 'NetQuantity']
    if not all(col in df.columns for col in required_cols):
        st.error(f"❗ 필수 컬럼이 없습니다: {required_cols}")
        st.stop()

    st.subheader("✅ 업로드한 데이터 미리보기")
    st.dataframe(df.head())

    result1 = detect_condition_1(df)
    result2 = detect_condition_2(df)
    result3 = detect_condition_3(df)
    returners = detect_heavy_returners(df)

    if 'TotalQuantity' in result1.columns:
        result1 = result1.sort_values(by='TotalQuantity', ascending=False)
    if 'TotalQuantity' in result2.columns:
        result2 = result2.sort_values(by='TotalQuantity', ascending=False)
    if 'TotalQuantity' in result3.columns:
        result3 = result3.sort_values(by='TotalQuantity', ascending=False)

    # ✅ 결과 출력 탭
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 조건 1", "🔍 조건 2", "🔍 조건 3", "↩️ 리턴 고객"])

    with tab1:
        st.markdown("**조건 1:** 동일 Article을 마지막 구매일 기준 365일 내 수량 2개 초과 구매")
        if 'SAPID' in result1.columns:
            st.write(f"위반 고객 수: {result1['SAPID'].nunique()}")
            st.dataframe(result1[['SAPID']].drop_duplicates())
        else:
            st.write("위반 고객이 없습니다.")

    with tab2:
        st.markdown("**조건 2:** 마지막 구매일 기준 30일 내 서로 다른 Article 5개 초과 구매")
        if 'SAPID' in result2.columns:
            st.write(f"위반 고객 수: {result2['SAPID'].nunique()}")
            st.dataframe(result2[['SAPID']].drop_duplicates())
        else:
            st.write("위반 고객이 없습니다.")

    with tab3:
        st.markdown("**조건 3:** 마지막 구매일 기준 365일 내 서로 다른 Article 10개 초과 구매")
        if 'SAPID' in result3.columns:
            st.write(f"위반 고객 수: {result3['SAPID'].nunique()}")
            st.dataframe(result3[['SAPID']].drop_duplicates())
        else:
            st.write("위반 고객이 없습니다.")

    with tab4:
        st.markdown("**리턴이 많은 고객 + Article별 리턴율**")
        if not returners.empty:
            st.write(f"리턴 고객 수: {returners['SAPID'].nunique()}")
            st.dataframe(returners)

            st.markdown("**📊 가장 많이 리턴된 Article Top 10**")
            top_articles = returners.groupby('Article')['ReturnQty'].sum().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots()
            top_articles.plot(kind='bar', ax=ax)
            ax.set_ylabel("Return Quantity")
            ax.set_xlabel("Article")
            ax.set_title("Top 10 Returned Articles")
            st.pyplot(fig)
        else:
            st.write("리턴 고객이 없습니다.")
else:
    st.info("👈 왼쪽에서 엑셀 파일을 업로드하세요.")
