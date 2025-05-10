import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import io
IMAGE_DIR = "image"
import os
from PIL import Image
import matplotlib.font_manager as fm
import io
import io
import io

# 월별 리턴 수량 텍스트 요약
for month, val in monthly_return_qty.items():
    # 평균 리턴율 요약
    for month, val in avg_return_rate.items():
        # Top 10 Article
        for article, qty in top_articles.items():
            # 차트 이미지 저장 및 삽입
            fig1.savefig(tmp1.name, dpi=100, bbox_inches='tight')
            fig2.savefig(tmp2.name, dpi=100, bbox_inches='tight')
            fig3.savefig(tmp3.name, dpi=100, bbox_inches='tight')
            fig4.savefig(tmp4.name, dpi=100, bbox_inches='tight')
            # 월별 리턴 수량 요약
            for month, val in monthly_return_qty.items():
                # 평균 리턴율 요약
                for month, val in avg_return_rate.items():
                    # Top 10 Article
                    for article, qty in top_articles.items():
def show_article_image(article):
    for ext in ['.jpg', '.jpeg', '.png']:
    pass

        if os.path.exists(path):
            st.image(Image.open(path), caption=f"Article: {article}", width=120)
            break
                                    plt.rcParams['font.family'] = 'Arial'  # Mac용 한글 폰트
                                    plt.rcParams['axes.unicode_minus'] = False
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
                                                                                    return_summary = return_df.groupby(['SAPID'])['NetQuantity'].sum().abs().reset_index()
                                                                                    return_summary.rename(columns={'NetQuantity': 'ReturnQty'}, inplace=True)
                                                                                    return_article_count = df[df['NetQuantity'] < 0].groupby('SAPID')['Article'].nunique()
                                                                                    purchase_article_count = df[df['NetQuantity'] > 0].groupby('SAPID')['Article'].nunique()
                                                                                    return_rate_by_sapid = (return_article_count / purchase_article_count).fillna(0)
                                                                                    return_summary['ReturnRate'] = return_summary['SAPID'].map(return_rate_by_sapid)
                                                                                    return return_summary.sort_values(by='ReturnQty', ascending=False)
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
                                                                                            mode = st.selectbox("🧭 모드를 선택하세요", ["탐지 모드", "리포트 모드"])
                                                                                            if mode == "탐지 모드":
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 조건 1", "🔍 조건 2", "🔍 조건 3", "↩️ 리턴 고객"])
            # ---- 탐지 조건 1 ----
        with tab1:
            if not result1.empty and 'SAPID' in result1.columns:
            pass
            st.markdown("**🖼 관련 이미지 (images/ 폴더 기준)**")
            for article in result1['Article'].unique():
            show_article_image(article)
else:
                                                                                                            st.write("위반 고객이 없습니다.")
                                                                                                            # ---- 탐지 조건 2 ----
    with tab2:
        if not result2.empty and 'SAPID' in result2.columns:
            pass
        st.markdown("**🖼 관련 이미지 (images/ 폴더 기준)**")
        for article in result2['Article'].unique():
        show_article_image(article)
    else:
                                                                                                                        st.write("위반 고객이 없습니다.")
                                                                                                                        # ---- 탐지 조건 3 ----
    with tab3:
        if not result3.empty and 'SAPID' in result3.columns:
            pass
        st.markdown("**🖼 관련 이미지 (images/ 폴더 기준)**")
        for article in result3['Article'].unique():
        show_article_image(article)
    else:
                                                                                                                                    st.write("위반 고객이 없습니다.")
                                                                                                                                    # ---- 탐지 조건 4 ----
    with tab4:
        st.markdown("**리턴 고객 요약 (SAPID 기준)**")
        total_customers = df['SAPID'].nunique()
        return_customers = returners['SAPID'].nunique()
        return_ratio = return_customers / total_customers * 100 if total_customers > 0 else 0
        st.write(f"✅ 리턴 이력이 있는 고객 수는 총 고객 {total_customers}명 중 {return_customers}명이며, {return_ratio:.1f}% 비중을 차지합니다.")
        if not returners.empty:
            pass
    else:
                                                                                                                                            st.write("리턴 고객이 없습니다.")
                                                                                                                                            st.markdown("**리턴 고객 요약 (SAPID 기준)**")
                                                                                                                                            total_customers = df['SAPID'].nunique()
                                                                                                                                            return_customers = returners['SAPID'].nunique()
                                                                                                                                            return_ratio = return_customers / total_customers * 100 if total_customers > 0 else 0
                                                                                                                                            st.write(f"✅ 리턴 이력이 있는 고객 수는 총 고객 {total_customers}명 중 {return_customers}명이며, {return_ratio:.1f}% 비중을 차지합니다.")
if True:
if mode == "탐지 모드":
    pass
    else mode == "리포트 모드":
    st.header("📊 리포트 모드: 월별 트렌드 요약")
    df['Month'] = df['PurchaseDate'].dt.to_period('M').astype(str)
    # 1. 월별 총 리턴 수량
    monthly_return_qty = df[df['NetQuantity'] < 0].groupby('Month')['NetQuantity'].sum().abs()
    st.subheader("📦 월별 총 리턴 수량")
    fig1, ax1 = plt.subplots(figsize=(8, 3.5))
    monthly_return_qty.plot(kind='bar', ax=ax1)
    for i, val in enumerate(monthly_return_qty):
    ax1.text(i, val, f"{val:.0f}", ha='center', va='bottom')
    st.pyplot(fig1)
    # 2. 월별 평균 리턴율
    return_articles = df[df['NetQuantity'] < 0].groupby(['SAPID', 'Month'])['Article'].nunique()
    purchase_articles = df[df['NetQuantity'] > 0].groupby(['SAPID', 'Month'])['Article'].nunique()
    return_rate = (return_articles / purchase_articles).fillna(0).reset_index(name='ReturnRate')
    avg_return_rate = return_rate.groupby('Month')['ReturnRate'].mean()
    st.subheader("📈 월별 평균 리턴율")
    fig2, ax2 = plt.subplots(figsize=(8, 3.5))
    avg_return_rate.plot(ax=ax2, marker='o')
    for i, val in enumerate(avg_return_rate):
    ax2.text(i, val, fontsize=8, f"{val:.2%}", ha='center', va='bottom')
    st.pyplot(fig2)
    # 3. 월별 조건별 위반율
    def compute_violation_rate(result_df, label):
    if result_df.empty:
    return pd.Series(dtype=float)
    temp = result_df.merge(df[['Article', 'PurchaseDate']], on='Article', how='left')
    temp['Month'] = temp['PurchaseDate'].dt.to_period('M').astype(str)
    rate = temp.groupby('Month')['SAPID'].nunique() / df.groupby('Month')['SAPID'].nunique()
    return rate.rename(label)
    cond1_rate = compute_violation_rate(result1, '조건 1')
    cond2_rate = compute_violation_rate(result2, '조건 2')
    cond3_rate = compute_violation_rate(result3, '조건 3')
    violation_df = pd.concat([cond1_rate, cond2_rate, cond3_rate], axis=1).fillna(0)
    st.subheader("📉 월별 조건별 위반율")
    fig3, ax3 = plt.subplots(figsize=(8, 3.5))
    violation_df.plot(ax=ax3, marker='o', legend=True)
    ax3.set_ylabel("비율 (%)", fontsize=8)
    ax3.set_xlabel("월", fontsize=8)
    ax3.tick_params(axis='x', labelrotation=45, labelsize=8)
    ax3.tick_params(axis='y', labelsize=8)
    ax3.legend(title="조건", fontsize=9, title_fontsize=10, loc='upper right')
    for line in ax3.lines:
    for x, y in zip(line.get_xdata(), line.get_ydata()):
    ax3.text(x, y, fontsize=8, f"{y:.1%}", ha='center', va='bottom', fontsize=8)
    st.pyplot(fig3)
    # 4. 가장 많이 리턴된 Article Top 10
    st.subheader("📌 가장 많이 리턴된 Article Top 10")
    # ✅ 계산 정의: 리턴 수량 기준 상위 10개 Article = NetQuantity < 0 인 값들의 합계를 기준으로 정렬
    top_articles = df[df['NetQuantity'] < 0].groupby('Article')['NetQuantity'].sum().abs().sort_values(ascending=False).head(10)
    fig4, ax4 = plt.subplots(figsize=(8, 3.5))
    top_articles.plot(kind='bar', ax=ax4)
    for i, val in enumerate(top_articles):
    ax4.text(i, val, fontsize=8, f"{val:.0f}", ha='center', va='bottom')
    ax4.set_ylabel("Return Quantity", fontsize=8)
    ax4.set_xlabel("Article", fontsize=8)
    ax4.set_title("Top 10 Returned Articles")
    st.pyplot(fig4)
    else:
    st.info("👈 왼쪽에서 엑셀 파일을 업로드하세요.")
    for month, val in monthly_return_qty.items():
    for month, val in avg_return_rate.items():
    for article, qty in top_articles.items():
    fig1.savefig(tmp1.name, dpi=100, bbox_inches='tight')
    fig2.savefig(tmp2.name, dpi=100, bbox_inches='tight')
    fig3.savefig(tmp3.name, dpi=100, bbox_inches='tight')
    fig4.savefig(tmp4.name, dpi=100, bbox_inches='tight')
    for month, val in monthly_return_qty.items():
    for month, val in avg_return_rate.items():
    for article, qty in top_articles.items():
    fig1.savefig(tmp1.name, dpi=100, bbox_inches='tight')
    fig2.savefig(tmp2.name, dpi=100, bbox_inches='tight')
    fig3.savefig(tmp3.name, dpi=100, bbox_inches='tight')
    fig4.savefig(tmp4.name, dpi=100, bbox_inches='tight')
