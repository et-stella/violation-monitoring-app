import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="커머셜 정책 위반 탐지기", page_icon="🛑", layout="wide")
st.title("🛑 커머셜 정책 위반 탐지기")
st.markdown("고객의 구매 수량을 기반으로 정책 위반 가능성을 분석합니다.")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"], key="file_upload_1")

# ✅ 조건 1: 마지막 구매일 기준 365일 수량 > 2
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

# ✅ 조건 2: 마지막 구매일 기준 30일 내 고유 Article 수 > 5
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

# ✅ 조건 3: 마지막 구매일 기준 365일 내 고유 Article 수 > 10
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

# ✅ 리턴 고객
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

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 조건 1", "🔍 조건 2", "🔍 조건 3", "↩️ 리턴]()
