
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from PIL import Image

# 설정
IMAGE_DIR = "image"
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False

def show_article_image(article):
    for ext in ['.jpg', '.jpeg', '.png']:
        path = os.path.join(IMAGE_DIR, f"{article}{ext}")
        if os.path.exists(path):
            st.image(Image.open(path), caption=f"Article: {article}", width=120)
            break

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
