import pandas as pd
import joblib

# Load trained model
model = joblib.load("road_risk_model.pkl")

# Sample route conditions
route_data = pd.DataFrame([
    {
        "weather": "rain",
        "road_type": "highway",
        "traffic_density": "high",
        "hour": 8,
        "is_peak_hour": 1,
        "visibility": "low",
        "temperature": 25,
        "lanes": 4
    }
])

# Predict risk
prediction = model.predict(route_data)[0]

# Convert to percentage
risk_percentage = prediction * 100

print("Predicted Risk Score:", round(prediction, 4))
print("Risk Percentage:", round(risk_percentage, 2), "%")

# Risk level
if prediction < 0.35:
    risk_level = "Low"
elif prediction < 0.65:
    risk_level = "Medium"
else:
    risk_level = "High"

print("Risk Level:", risk_level)
