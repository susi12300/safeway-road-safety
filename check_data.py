import pandas as pd

# Read the accident dataset
data = pd.read_csv("accident_data.csv")

# Show the first 5 rows
print("\nFirst 5 rows:")
print(data.head())

# Show all column names
print("\nColumn names:")
print(data.columns.tolist())

# Show the number of rows and columns
print("\nDataset size:")
print(data.shape)

# Show missing values
print("\nMissing values:")
print(data.isnull().sum())