def generate_report(df):
    total = len(df)
    suspicious = df['suspicious'].sum()
    clean = total - suspicious

    report = f"""
===== Poison Detection Report =====
Total Samples: {total}
Suspicious Samples: {suspicious}
Clean Samples: {clean}
Detection Rate: {(suspicious/total)*100:.2f}%
"""

    with open("../output/report.txt", "w") as f:
        f.write(report)