import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from src.auth import login, signup

st.set_page_config(page_title="PoisonGuard AI", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "custom_model" not in st.session_state:
    st.session_state.custom_model = None


# ---------------- AUTH ----------------
def auth_page():
    st.title("🔐 PoisonGuard AI")

    choice = st.sidebar.selectbox("Menu", ["Login", "Signup"])

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful")
            else:
                st.error("Invalid credentials")

    else:
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Signup"):
            if signup(new_user, new_pass):
                st.success("Account created")
            else:
                st.error("Error creating account")


# ---------------- HELPERS ----------------
def load_data(file):
    try:
        return pd.read_csv(file, encoding='utf-8')
    except:
        try:
            return pd.read_csv(file, encoding='latin-1')
        except:
            return pd.read_csv(file, encoding='ISO-8859-1')


def analyze(df):
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.shape[1] == 0:
        df['iso_flag'] = False
    else:
        if st.session_state.custom_model:
            model = st.session_state.custom_model
            preds = model.predict(numeric_df)
        else:
            model = IsolationForest(contamination=0.2, random_state=42)
            preds = model.fit_predict(numeric_df)

        df['iso_flag'] = preds == -1

    # Rule-based detection
    def rule_check(row):
        text = str(row).lower()
        if "free" in text or "win" in text or "money" in text:
            return True
        return False

    df['rule_flag'] = df.apply(rule_check, axis=1)
    df['suspicious'] = df['iso_flag'] | df['rule_flag']

    suspicious = df[df['suspicious'] == True]
    clean = df[df['suspicious'] == False]

    risk = (len(suspicious) / len(df)) * 100

    return df, suspicious, clean, risk


# ---------------- MAIN APP ----------------
def main_app():
    if "username" not in st.session_state:
        st.warning("Login required")
        st.stop()

    st.title("🛡️ PoisonGuard AI Dashboard")
    st.markdown(f"### 👋 Welcome, {st.session_state.username}")

    # ---------------- TRAIN MODEL ----------------
    st.subheader("🤖 Train Custom Model")

    train_file = st.file_uploader("Upload Training Dataset", type=["csv"], key="train")

    if train_file:
        train_df = load_data(train_file)
        st.dataframe(train_df.head())

        if st.button("🚀 Train Model"):
            numeric_df = train_df.select_dtypes(include=[np.number])

            if numeric_df.shape[1] == 0:
                st.error("❌ No numeric columns found")
            else:
                model = IsolationForest(contamination=0.2, random_state=42)
                model.fit(numeric_df)
                st.session_state.custom_model = model
                st.success("✅ Custom model trained!")

    # ---------------- UPLOAD + COMPARE ----------------
    st.subheader("📁 Upload & Compare Datasets")

    colA, colB = st.columns(2)

    file1 = colA.file_uploader("Upload Dataset 1", type=["csv"], key="file1")
    file2 = colB.file_uploader("Upload Dataset 2", type=["csv"], key="file2")

    # ---------------- SINGLE FILE ----------------
    if file1 and not file2:
        df = load_data(file1)
        result, suspicious, clean_data, risk = analyze(df)

        st.subheader("📊 Analysis Result")

        st.metric("Risk %", f"{risk:.2f}")
        st.dataframe(result)

    # ---------------- COMPARE ----------------
    if file1 and file2:
        df1 = load_data(file1)
        df2 = load_data(file2)

        result1, sus1, clean1, risk1 = analyze(df1)
        result2, sus2, clean2, risk2 = analyze(df2)

        st.subheader("⚔️ Dataset Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📂 Dataset 1")
            st.metric("Risk %", f"{risk1:.2f}")
            st.metric("Suspicious Rows", len(sus1))
            st.dataframe(sus1.head())

        with col2:
            st.markdown("### 📂 Dataset 2")
            st.metric("Risk %", f"{risk2:.2f}")
            st.metric("Suspicious Rows", len(sus2))
            st.dataframe(sus2.head())

        st.subheader("🏆 Final Verdict")

        if risk1 < risk2:
            st.success("✅ Dataset 1 is SAFER")
        elif risk2 < risk1:
            st.success("✅ Dataset 2 is SAFER")
        else:
            st.info("⚖️ Both datasets equal risk")

        st.bar_chart({
            "Dataset 1": risk1,
            "Dataset 2": risk2
        })

    # ---------------- LOGOUT ----------------
    if st.button("Logout"):
        st.session_state.logged_in = False


# ---------------- ROUTER ----------------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()