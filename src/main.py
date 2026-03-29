import pandas as pd
import matplotlib.pyplot as plt
from detector import detect_anomalies
from utils import generate_report

# LOAD DATA
df = pd.read_csv("../data/dataset.csv")

# DETECT
result = detect_anomalies(df)

# SAVE OUTPUT
result.to_csv("../output/cleaned_data.csv", index=False)

# REPORT
generate_report(result)

# PRINT RESULT
print("\n===== RESULT =====")
print(result[['age', 'salary', 'label', 'suspicious']])

# GRAPH
result['suspicious'].value_counts().plot(kind='bar')
plt.title("Poison Detection Result")
plt.xlabel("False = Clean | True = Suspicious")
plt.ylabel("Count")
plt.show()

print("\n✅ DONE! Check output folder.")