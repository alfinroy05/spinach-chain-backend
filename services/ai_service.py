import numpy as np
from statistics import mean, stdev


# 🔹 Feature Engineering
def extract_features(sensor_data):
    temperatures = [d["temperature"] for d in sensor_data]
    humidity = [d["humidity"] for d in sensor_data]
    moisture = [d["soil_moisture"] for d in sensor_data]
    nitrogen = [d["nitrogen"] for d in sensor_data]
    phosphorus = [d["phosphorus"] for d in sensor_data]
    potassium = [d["potassium"] for d in sensor_data]

    features = {
        "avg_temp": mean(temperatures),
        "avg_humidity": mean(humidity),
        "avg_moisture": mean(moisture),
        "avg_n": mean(nitrogen),
        "avg_p": mean(phosphorus),
        "avg_k": mean(potassium),
        "temp_variation": stdev(temperatures) if len(temperatures) > 1 else 0,
    }

    return features


# 🔹 Anomaly Detection (Simple Statistical)
def detect_anomaly(features):
    anomaly = False

    if features["avg_temp"] > 35:
        anomaly = True

    if features["avg_moisture"] < 20:
        anomaly = True

    if features["temp_variation"] > 10:
        anomaly = True

    return anomaly


# 🔹 Yield Prediction (Simulated ML Formula)
def predict_yield(features):
    yield_estimate = (
        features["avg_moisture"] * 0.6 +
        features["avg_n"] * 1.5 +
        features["avg_p"] * 1.2 +
        features["avg_k"] * 1.3
    )

    return round(yield_estimate, 2)


# 🔹 Disease Probability Model
def predict_disease(features):
    probability = 0.0

    if features["avg_temp"] > 32 and features["avg_humidity"] > 70:
        probability = 0.75
    elif features["avg_moisture"] < 25:
        probability = 0.5
    elif features["avg_temp"] > 30:
        probability = 0.3

    return round(probability, 2)


# 🔹 Health Score (0–100)
def calculate_health_score(disease_probability, anomaly):
    base_score = 100 - (disease_probability * 100)

    if anomaly:
        base_score -= 15

    return max(0, round(base_score, 2))


# 🔥 MAIN AI ENTRY FUNCTION
def run_ai_analysis(sensor_data):
    if not sensor_data:
        return {
            "predicted_yield": 0,
            "disease_probability": 0,
            "health_score": 0,
            "anomaly_detected": False
        }

    features = extract_features(sensor_data)

    anomaly = detect_anomaly(features)

    predicted_yield = predict_yield(features)

    disease_probability = predict_disease(features)

    health_score = calculate_health_score(disease_probability, anomaly)

    return {
        "predicted_yield": predicted_yield,
        "disease_probability": disease_probability,
        "health_score": health_score,
        "anomaly_detected": anomaly
    }