import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="커머셜 정책 위반 탐지기", page_icon="🛑", layout="wide")
st.title("🛑 커머셜 정책 위반 탐지기")
st.markdown("고객의 구매 수량을 기반으로 정책 위반 가능성을 분석합니다.")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"], key="file_upload_1")

# 조건 함수 정의
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
    return_summary = return_df.groupby(['SAPID', 'Article'])['NetQuantity'].sum().reset_index()
    return_summary['ReturnQty'] = return_summary['NetQuantity'].abs()
    total_purchase = df[df['NetQuantity'] > 0].groupby(['SAPID', 'Article'])['NetQuantity'].sum().reset_index()
    merged = pd.merge(return_summary, total_purchase, on=['SAPID', 'Article'], how='left', suffixes=('_Return', '_Purchase'))
    merged['ReturnRate'] = merged['ReturnQty'] / merged['NetQuantity_Purchase']
    merged = merged.drop(columns=['NetQuantity_Return', 'NetQuantity_Purchase'])
    merged = merged[merged['ReturnRate'].notna()].sort_values(by='ReturnQty', ascending=False)
    return merged

# 실행
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

    # 모드 선택
    mode = st.selectbox("🧭 모드를 선택하세요", ["탐지 모드", "리포트 모드"])

    if mode == "탐지 모드":
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 조건 1", "🔍 조건 2", "🔍 조건 3", "↩️ 리턴 고객"])

        with tab1:
            st.markdown("**조건 1:** 동일 Article을 마지막 구매일 기준 365일 내 수량 2개 초과 구매")
            if 'SAPID' in result1.columns:
                selected_sapid = st.selectbox("고객 선택 (조건 1)", result1['SAPID'].unique())
                st.dataframe(result1[result1['SAPID'] == selected_sapid])
            else:
                st.write("위반 고객이 없습니다.")

        with tab2:
            st.markdown("**조건 2:** 마지막 구매일 기준 30일 내 서로 다른 Article 5개 초과 구매")
            if 'SAPID' in result2.columns:
                selected_sapid = st.selectbox("고객 선택 (조건 2)", result2['SAPID'].unique())
                st.dataframe(result2[result2['SAPID'] == selected_sapid])
            else:
                st.write("위반 고객이 없습니다.")

        with tab3:
            st.markdown("**조건 3:** 마지막 구매일 기준 365일 내 서로 다른 Article 10개 초과 구매")
            if 'SAPID' in result3.columns:
                selected_sapid = st.selectbox("고객 선택 (조건 3)", result3['SAPID'].unique())
                st.dataframe(result3[result3['SAPID'] == selected_sapid])
            else:
                st.write("위반 고객이 없습니다.")

        with tab4:
            st.markdown("**리턴이 많은 고객 요약**")
            if not returners.empty:
                return_article_count = df[df['NetQuantity'] < 0].groupby('SAPID')['Article'].nunique()
                purchase_article_count = df[df['NetQuantity'] > 0].groupby('SAPID')['Article'].nunique()
                return_rate_by_sapid = (return_article_count / purchase_article_count).fillna(0)

                return_summary = returners.groupby('SAPID')['ReturnQty'].sum().reset_index()
                return_summary['ReturnRate'] = return_summary['SAPID'].map(return_rate_by_sapid)

                selected_sapid = st.selectbox("고객 선택 (리턴)", return_summary['SAPID'].unique())
                st.dataframe(return_summary[return_summary['SAPID'] == selected_sapid])
            else:
                st.write("리턴 고객이 없습니다.")

    elif mode == "리포트 모드":
        st.header("📊 리포트 모드: 월별 트렌드 요약")

        df['Month'] = df['PurchaseDate'].dt.to_period('M').astype(str)

        monthly_return_qty = df[df['NetQuantity'] < 0].groupby('Month')['NetQuantity'].sum().abs()
        st.subheader("📦 월별 총 리턴 수량")
        st.bar_chart(monthly_return_qty)

        return_articles = df[df['NetQuantity'] < 0].groupby(['SAPID', 'Month'])['Article'].nunique()
        purchase_articles = df[df['NetQuantity'] > 0].groupby(['SAPID', 'Month'])['Article'].nunique()
        return_rate = (return_articles / purchase_articles).fillna(0).reset_index()
        avg_return_rate = return_rate.groupby('Month')[0].mean()
        st.subheader("📈 월별 평균 리턴율")
        st.line_chart(avg_return_rate)

        def compute_violation_rate(result_df, label):
            if result_df.empty:
                return pd.Series(dtype=float)
            temp = result_df.copy()
            temp = temp.merge(df[['Article', 'PurchaseDate']], on='Article', how='left')
            temp['Month'] = temp['PurchaseDate'].dt.to_period('M').astype(str)
            rate = temp.groupby('Month')['SAPID'].nunique() / df.groupby('Month')['SAPID'].nunique()
            return rate.rename(label)

        cond1_rate = compute_violation_rate(result1, '조건 1')
        cond2_rate = compute_violation_rate(result2, '조건 2')
        cond3_rate = compute_violation_rate(result3, '조건 3')

        violation_df = pd.concat([cond1_rate, cond2_rate, cond3_rate], axis=1).fillna(0)

        st.subheader("📉 월별 조건별 위반율")
        st.line_chart(violation_df)
else:
    st.info("👈 왼쪽에서 엑셀 파일을 업로드하세요.")
