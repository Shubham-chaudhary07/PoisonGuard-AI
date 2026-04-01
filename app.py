import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from src.auth import login, signup

st.set_page_config(page_title="PoisonGuard AI", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "custom_model" not in st.session_state:
    st.session_state.custom_model = None

if "vectorizer" not in st.session_state:
    st.session_state.vectorizer = None

if "trained_columns" not in st.session_state:
    st.session_state.trained_columns = None


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


# ---------------- LOAD DATA ----------------
def load_data(file):
    try:
        return pd.read_csv(file, encoding='utf-8')
    except:
        try:
            return pd.read_csv(file, encoding='latin-1')
        except:
            return pd.read_csv(file, encoding='ISO-8859-1')


# ---------------- ANALYZE ----------------
def analyze(df):
    df = df.copy()
    numeric_df = df.select_dtypes(include=[np.number])

    model = st.session_state.custom_model
    trained_cols = st.session_state.trained_columns

    if model is not None and trained_cols is not None:
        for col in trained_cols:
            if col not in numeric_df.columns:
                numeric_df[col] = 0

        numeric_df = numeric_df[trained_cols]

        try:
            preds = model.predict(numeric_df)
            df['iso_flag'] = preds == -1
        except:
            df['iso_flag'] = False
    else:
        if numeric_df.shape[1] > 0:
            model = IsolationForest(contamination=0.1, random_state=42)
            preds = model.fit_predict(numeric_df)
            df['iso_flag'] = preds == -1
        else:
            df['iso_flag'] = False

    def rule_check(row):
        text = str(row).lower()
        keywords = ["free", "win", "money", "offer", "urgent", "click"]
        return any(word in text for word in keywords)

    df['rule_flag'] = df.apply(rule_check, axis=1)
    df['suspicious'] = df['iso_flag'] | df['rule_flag']

    suspicious = df[df['suspicious']]
    clean = df[~df['suspicious']]
    risk = (len(suspicious) / len(df)) * 100 if len(df) > 0 else 0

    return df, suspicious, clean, risk


# ---------------- MAIN ----------------
def main_app():
    st.title("🛡️ PoisonGuard AI Dashboard")
    st.markdown(f"### 👋 Welcome, {st.session_state.username}")

    # MODEL
    st.subheader("⚙️ Model Selection")
    model_type = st.selectbox("Choose Model", ["Auto", "Numeric", "Text"])

    # ---------------- TRAIN ----------------
    st.subheader("🤖 Train Model")

    train_file = st.file_uploader("Upload Training Dataset", type=["csv"], key="train")

    if train_file:
        train_df = load_data(train_file)
        st.dataframe(train_df.head())

        if st.button("🚀 Train Model"):
            numeric_df = train_df.select_dtypes(include=[np.number])

            if model_type in ["Auto", "Numeric"] and numeric_df.shape[1] > 0:
                model = IsolationForest(contamination=0.1, random_state=42)
                model.fit(numeric_df)

                st.session_state.custom_model = model
                st.session_state.trained_columns = list(numeric_df.columns)
                st.session_state.vectorizer = None

                st.success("✅ Numeric Model Trained!")

            elif model_type == "Text" and 'text' in train_df.columns:
                vectorizer = TfidfVectorizer(max_features=100)
                X = vectorizer.fit_transform(train_df['text'].astype(str))

                model = IsolationForest(contamination=0.1, random_state=42)
                model.fit(X)

                st.session_state.custom_model = model
                st.session_state.vectorizer = vectorizer
                st.session_state.trained_columns = None

                st.success("✅ Text Model Trained!")

            else:
                st.error("❌ Dataset not suitable")

    # ---------------- COMPARE ----------------
    st.subheader("📊 Compare Two Datasets")

    col1, col2 = st.columns(2)

    file1 = col1.file_uploader("Upload Dataset 1", type=["csv"], key="f1")
    file2 = col2.file_uploader("Upload Dataset 2", type=["csv"], key="f2")

    if file1 and file2:
        df1 = load_data(file1)
        df2 = load_data(file2)

        _, _, _, risk1 = analyze(df1)
        _, _, _, risk2 = analyze(df2)

        col1.metric("Dataset 1 Risk", f"{risk1:.2f}%")
        col2.metric("Dataset 2 Risk", f"{risk2:.2f}%")

        st.bar_chart({
            "Dataset 1": risk1,
            "Dataset 2": risk2
        })

    # ---------------- SINGLE ANALYSIS ----------------
    st.subheader("📁 Analyze Single Dataset")

    file = st.file_uploader("Upload Dataset", type=["csv"], key="single")

    if file:
        df = load_data(file)
        result, sus, clean, risk = analyze(df)

        st.metric("Risk %", f"{risk:.2f}%")

        st.write("📊 Full Data")
        st.dataframe(result)

        st.write("🚨 Suspicious Data")
        st.dataframe(sus)

        st.write("✅ Clean Data")
        st.dataframe(clean)

        # ---------------- DOWNLOAD ----------------
        st.subheader("📥 Download Results")

        clean_csv = clean.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Clean Data", clean_csv, "clean.csv", "text/csv")

        sus_csv = sus.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Suspicious Data", sus_csv, "suspicious.csv", "text/csv")

        # ---------------- PDF REPORT ----------------
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        def generate_pdf():
            doc = SimpleDocTemplate("report.pdf")
            styles = getSampleStyleSheet()

            content = []
            content.append(Paragraph("PoisonGuard AI Report", styles['Title']))
            content.append(Spacer(1, 12))
            content.append(Paragraph(f"Total Records: {len(df)}", styles['Normal']))
            content.append(Paragraph(f"Suspicious Records: {len(sus)}", styles['Normal']))
            content.append(Paragraph(f"Risk: {risk:.2f}%", styles['Normal']))

            doc.build(content)

            with open("report.pdf", "rb") as f:
                return f.read()

        if st.button("📄 Generate Report"):
            pdf = generate_pdf()
            st.download_button("⬇️ Download PDF", pdf, "report.pdf")

    if st.button("Logout"):
        st.session_state.logged_in = False


# ---------------- ROUTER ----------------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()