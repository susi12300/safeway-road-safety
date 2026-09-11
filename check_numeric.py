import pandas as pd

data = pd.read_csv("accident_data.csv")

columns_to_check = [
    "hour",
    "temperature",
    "lanes",
    "risk_score"
]

for column in columns_to_check:
    print("\n" + "=" * 40)
    print(column.upper())
    print(data[column].describe())