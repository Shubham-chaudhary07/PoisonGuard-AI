st.subheader("📊 Model Performance Evaluation")

eval_file = st.file_uploader("Upload Test Dataset (with labels)", type=["csv"], key="eval")

if eval_file:
    eval_df = load_data(eval_file)
    st.write("📊 Test Data Preview")
    st.dataframe(eval_df.head())

    if st.button("📈 Evaluate Model"):

        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        import seaborn as sns
        import matplotlib.pyplot as plt

        if 'label' not in eval_df.columns:
            st.error("❌ Dataset must contain 'label' column (safe / suspicious)")
        else:
            # 🧠 Run prediction
            result, _, _, _ = analyze(eval_df)

            # Convert labels
            y_true = eval_df['label'].apply(lambda x: 1 if str(x).lower() in ["1", "true", "suspicious", "spam"] else 0)
            y_pred = result['suspicious'].apply(lambda x: 1 if x else 0)

            # 📊 Metrics
            acc = accuracy_score(y_true, y_pred)
            prec = precision_score(y_true, y_pred, zero_division=0)
            rec = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)

            # 🎯 Show Metrics
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Accuracy", f"{acc:.2f}")
            col2.metric("Precision", f"{prec:.2f}")
            col3.metric("Recall", f"{rec:.2f}")
            col4.metric("F1 Score", f"{f1:.2f}")

            # 📉 Confusion Matrix
            cm = confusion_matrix(y_true, y_pred)

            fig, ax = plt.subplots()
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)

            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            ax.set_title("Confusion Matrix")

            st.pyplot(fig)