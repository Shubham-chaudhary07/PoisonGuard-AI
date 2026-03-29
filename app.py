import streamlit as st
import pandas as pd
from src.auth import login, signup
from src.detector import detect_anomalies
from src.dataset_db import save_dataset, get_user_datasets

st.set_page_config(page_title="PoisonGuard AI", layout="wide")

# SESSION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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
                st.error("User already exists")


# ---------------- MAIN APP ----------------
def main_app():
    if "username" not in st.session_state:
        st.warning("Login required")
        st.stop()

    st.title("🛡️ PoisonGuard AI Dashboard")
    st.markdown(f"### 👋 Welcome, {st.session_state.username}")

    uploaded_file = st.file_uploader("📂 Upload Dataset", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        result = detect_anomalies(df)

        suspicious = result[result['suspicious'] == True]
        clean_data = result[result['suspicious'] == False]

        risk = (len(suspicious)/len(result))*100

        # ALERT
        if risk > 30:
            st.error("🚨 High Risk Dataset!")
        elif risk > 10:
            st.warning("⚠️ Medium Risk")
        else:
            st.success("✅ Safe Dataset")

        # METRICS
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", len(result))
        col2.metric("Threats", len(suspicious))
        col3.metric("Safe", len(clean_data))
        col4.metric("Risk %", f"{risk:.2f}")

        # SAVE DATASET
        save_dataset(
            st.session_state.username,
            uploaded_file.name,
            len(result),
            len(suspicious),
            risk
        )

        # TABS
        tab1, tab2, tab3 = st.tabs(["🚨 Suspicious", "✅ Clean", "📊 Full"])

        with tab1:
            st.dataframe(suspicious)

        with tab2:
            st.dataframe(clean_data)

        with tab3:
            st.dataframe(result)

        st.download_button(
            "Download Clean Data",
            clean_data.to_csv(index=False),
            "clean.csv"
        )

    # HISTORY
    st.subheader("📁 Dataset History")

    data = get_user_datasets(st.session_state.username)

    if data:
        history_df = pd.DataFrame(data, columns=[
            "Filename", "Total Rows", "Threats", "Risk %", "Upload Time"
        ])
        st.dataframe(history_df)
    else:
        st.info("No datasets yet")

    if st.button("Logout"):
        st.session_state.logged_in = False


# ROUTER
if st.session_state.logged_in:
    main_app()
else:
    auth_page()