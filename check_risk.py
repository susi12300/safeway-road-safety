import pandas as pd

data = pd.read_csv("accident_data.csv")

print("Risk Score Details:")
print(data["risk_score"].describe())

print("\nFirst 10 Risk Scores:")
print(data["risk_score"].head(10))

print("\nRisk Score Missing Values:")
print(data["risk_score"].isnull().sum())

print("\nRisk Score Range:")
print("Minimum:", data["risk_score"].min())
print("Maximum:", data["risk_score"].max())
print("\nAverage risk based on number of vehicles involved:")

print(
    data.groupby("vehicles_involved")["risk_score"].mean()
)