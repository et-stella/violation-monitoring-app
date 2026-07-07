import streamlit as st
import pandas as pd

st.set_page_config(page_title="Commercial Policy Violation Monitor", page_icon="🛑", layout="wide")
st.title("🛑 Commercial Policy Violation Monitor")
uploaded_file=st.file_uploader("엑셀 파일 업로드",type=["xlsx"])

REQUIRED_COLS=["Sap Order ID","Purchase Date","Return ID","Article","PCS"]

def prepare_data(df):
    missing=[c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        st.error(f"필수 컬럼이 없습니다: {missing}")
        st.stop()
    df=df.copy()
    df["Customer ID"]=df["Sap Order ID"].astype(str)
    df["Purchase Date"]=pd.to_datetime(df["Purchase Date"],errors="coerce")
    df["PCS"]=pd.to_numeric(df["PCS"],errors="coerce").fillna(0)
    df["Is Return"]=df["Return ID"].fillna("").astype(str).str.strip()!=""
    df["Adjusted PCS"]=df["PCS"]
    df.loc[df["Is Return"],"Adjusted PCS"]=-df.loc[df["Is Return"],"PCS"].abs()
    return df

def detect(df,group_cols,days,threshold,article_level):
    out=[]
    for key,g in df.groupby(group_cols):
        g=g.sort_values("Purchase Date")
        for _,r in g.iterrows():
            end=r["Purchase Date"]
            start=end-pd.Timedelta(days=days)
            w=g[(g["Purchase Date"]>=start)&(g["Purchase Date"]<=end)]
            net=w["Adjusted PCS"].sum()
            if net>threshold:
                if article_level:
                    cid,article=key
                else:
                    cid=key
                    article="ALL"
                out.append({"Customer ID":cid,"Article":article,"Net PCS":net})
                break
    return pd.DataFrame(out)

if uploaded_file:
    df=prepare_data(pd.read_excel(uploaded_file))
    c1=detect(df,["Customer ID","Article"],365,2,True)
    c2=detect(df,["Customer ID"],365,10,False)
    c3=detect(df,["Customer ID"],30,5,False)
    t1,t2,t3,t4=st.tabs(["Condition1","Condition2","Condition3","Returns"])
    with t1:
        st.dataframe(c1)
    with t2:
        st.dataframe(c2)
    with t3:
        st.dataframe(c3)
    with t4:
        return_df=df[df["Is Return"]]
        if return_df.empty:
            st.info("반품 데이터가 없습니다.")
        else:
            st.dataframe(return_df)
else:
    st.info("엑셀 파일을 업로드하세요.")
