
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
plt.rcParams['font.family'] = 'arial'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="커머셜 정책 위반 탐지기", page_icon="🛑", layout="wide")
st.title("🛑 커머셜 정책 위반 탐지기")
st.markdown("고객의 구매 수량을 기반으로 정책 위반 가능성을 분석합니다.")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"], key="file_upload_1")

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

def detect_heavy_returners(df):
    return_df = df[df['NetQuantity'] < 0]
    return_summary = return_df.groupby(['SAPID'])['NetQuantity'].sum().abs().reset_index()
    return_summary.rename(columns={'NetQuantity': 'ReturnQty'}, inplace=True)

    return_article_count = df[df['NetQuantity'] < 0].groupby('SAPID')['Article'].nunique()
    purchase_article_count = df[df['NetQuantity'] > 0].groupby('SAPID')['Article'].nunique()
    return_rate_by_sapid = (return_article_count / purchase_article_count).fillna(0)

    return_summary['ReturnRate'] = return_summary['SAPID'].map(return_rate_by_sapid)
    return return_summary.sort_values(by='ReturnQty', ascending=False)

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

    mode = st.selectbox("🧭 모드를 선택하세요", ["탐지 모드", "리포트 모드"])

    if mode == "탐지 모드":
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 조건 1", "🔍 조건 2", "🔍 조건 3", "↩️ 리턴 고객"])
        with tab1:
            st.markdown("**조건 1 Raw 결과**")
            if not result1.empty and 'SAPID' in result1.columns:
                st.write(f"✅ 조건 1 위반 고객 수: {result1['SAPID'].nunique()}명")
                st.dataframe(result1.reset_index(drop=True))
            else:
                st.write("위반 고객이 없습니다.")
        with tab2:
            st.markdown("**조건 2 Raw 결과**")
            if not result2.empty and 'SAPID' in result2.columns:
                st.write(f"✅ 조건 2 위반 고객 수: {result2['SAPID'].nunique()}명")
                st.dataframe(result2.reset_index(drop=True))
            else:
                st.write("위반 고객이 없습니다.")
        with tab3:
            st.markdown("**조건 3 Raw 결과**")
            if not result3.empty and 'SAPID' in result3.columns:
                st.write(f"✅ 조건 3 위반 고객 수: {result3['SAPID'].nunique()}명")
                st.dataframe(result3.reset_index(drop=True))
            else:
                st.write("위반 고객이 없습니다.")
        with tab4:
            st.markdown("**리턴 고객 요약 (SAPID 기준)**")
            total_customers = df['SAPID'].nunique()
            return_customers = returners['SAPID'].nunique()
            return_ratio = return_customers / total_customers * 100 if total_customers > 0 else 0
            st.write(f"✅ 리턴 이력이 있는 고객 수는 총 고객 {total_customers}명 중 {return_customers}명이며, {return_ratio:.1f}% 비중을 차지합니다.")
            st.dataframe(returners.reset_index(drop=True))
else:
    st.info("👈 왼쪽에서 엑셀 파일을 업로드하세요.")
