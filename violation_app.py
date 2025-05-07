import streamlit as st
import pandas as pd

st.set_page_config(page_title="커머셜 정책 위반 탐지기", page_icon="🛑", layout="wide")
st.title("🛑 커머셜 정책 위반 탐지기")
st.markdown("업로드된 구매 데이터를 기반으로 고객의 정책 위반 여부를 분석합니다.")

# 📁 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"], key="file_upload_1")

# 🧠 함수 정의 (롤링 조건 적용)
def detect_condition_1(df):
    result = set()
    for (sap, article), group in df.groupby(['SAPID', 'Article']):
        group = group.sort_values('PurchaseDate')
        for date in group['PurchaseDate']:
            count = group[(group['PurchaseDate'] >= date - pd.Timedelta(days=365)) &
                          (group['PurchaseDate'] <= date)].shape[0]
            if count > 2:  # 동일 Article 3회 이상
                result.add(sap)
                break
    return sorted(list(result))

def detect_condition_2(df):
    result = set()
    for sap, group in df.groupby('SAPID'):
        group = group.sort_values('PurchaseDate')
        for date in group['PurchaseDate']:
            window = group[(group['PurchaseDate'] >= date - pd.Timedelta(days=30)) &
                           (group['PurchaseDate'] <= date)]
            if window['ProductReference'].nunique() > 5:  # 5개 초과
                result.add(sap)
                break
    return sorted(list(result))

def detect_condition_3(df):
    result = set()
    for sap, group in df.groupby('SAPID'):
        group = group.sort_values('PurchaseDate')
        for date in group['PurchaseDate']:
            window = group[(group['PurchaseDate'] >= date - pd.Timedelta(days=365)) &
                           (group['PurchaseDate'] <= date)]
            if window['ProductReference'].nunique() > 10:  # 10개 초과
                result.add(sap)
                break
    return sorted(list(result))

# ✅ 실행 로직
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')

    # 필수 컬럼 체크
    required_cols = ['SAPID', 'Article', 'ProductReference', 'PurchaseDate']
    if not all(col in df.columns for col in required_cols):
        st.error(f"❗ 필수 컬럼이 없습니다: {required_cols}")
        st.stop()

    st.subheader("✅ 업로드한 데이터 미리보기")
    st.dataframe(df.head())

    # 조건별 탐지 실행
    result1 = detect_condition_1(df)
    result2 = detect_condition_2(df)
    result3 = detect_condition_3(df)

    # 결과 출력
    tab1, tab2, tab3 = st.tabs(["🔍 조건 1", "🔍 조건 2", "🔍 조건 3"])

    with tab1:
        st.markdown("**조건 1:** 동일 Article을 365일 내 3회 초과 구매한 고객")
        st.write(f"위반 고객 수: {len(result1)}명")
        st.dataframe(pd.DataFrame(result1, columns=["SAPID"]))

    with tab2:
        st.markdown("**조건 2:** 30일 내 5개 초과 ProductReference 구매한 고객")
        st.write(f"위반 고객 수: {len(result2)}명")
        st.dataframe(pd.DataFrame(result2, columns=["SAPID"]))

    with tab3:
        st.markdown("**조건 3:** 365일 내 10개 초과 ProductReference 구매한 고객")
        st.write(f"위반 고객 수: {len(result3)}명")
        st.dataframe(pd.DataFrame(result3, columns=["SAPID"]))

else:
    st.info("👈 왼쪽에서 엑셀 파일을 업로드하세요.")

