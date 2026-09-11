import pandas as pd

data = pd.read_csv("accident_data.csv")

columns_to_check = [
    "weather",
    "road_type",
    "traffic_density",
    "accident_severity",
    "is_peak_hour",
    "visibility"
]

for column in columns_to_check:
    print("\n" + "=" * 40)
    print(column.upper())
    print(data[column].value_counts())