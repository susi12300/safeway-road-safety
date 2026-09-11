import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib


# Load dataset
data = pd.read_csv("accident_data.csv")


# Select input features
features = [
    "weather",
    "road_type",
    "traffic_density",
    "hour",
    "is_peak_hour",
    "visibility",
    "temperature",
    "lanes"
]

X = data[features]

# Target column
y = data["risk_score"]


# Separate text and numeric columns
categorical_features = [
    "weather",
    "road_type",
    "traffic_density",
    "visibility"
]

numeric_features = [
    "hour",
    "is_peak_hour",
    "temperature",
    "lanes"
]


# Convert text values into numbers
preprocessor = ColumnTransformer(
    transformers=[
        (
            "category",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "number",
            "passthrough",
            numeric_features
        )
    ]
)


# Create ML model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# Create complete pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# Train model
pipeline.fit(X_train, y_train)


# Test model
predictions = pipeline.predict(X_test)


# Calculate performance
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)


print("Model training completed!")

print("\nMean Absolute Error:", round(mae, 4))
print("R2 Score:", round(r2, 4))


# Save trained model
joblib.dump(
    pipeline,
    "road_risk_model.pkl"
)

print("\nModel saved as road_risk_model.pkl")
import pandas as pd

data = pd.read_csv("accident_data.csv")

print(
    data.groupby("road_type")["risk_score"].agg(
        ["count", "mean", "min", "max"]
    )
)