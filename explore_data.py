import pandas as pd

data = pd.read_csv("accident_data.csv")

print("Dataset Shape:")
print(data.shape)

print("\nTamil Nadu accidents:")
tn_data = data[data["state"] == "Tamil Nadu"]
print(tn_data.shape)

print("\nCities in Tamil Nadu:")
print(tn_data["city"].unique())

print("\nWeather values:")
print(data["weather"].unique())

print("\nAccident Severity values:")
print(data["accident_severity"].unique())

print("\nMissing values:")
print(data.isnull().sum())