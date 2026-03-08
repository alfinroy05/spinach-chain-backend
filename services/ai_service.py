import os
import numpy as np
import tensorflow as tf
import joblib
from PIL import Image
from statistics import mean
from datetime import datetime
from tensorflow.keras.applications.efficientnet import preprocess_input


# =====================================================
# 🔥 SAFE MODEL LOADING (Singleton Style)
# =====================================================

# =====================================================
# 🔥 CORRECT PROJECT ROOT PATH
# =====================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOMATO_MODEL_PATH = os.path.join(PROJECT_ROOT, "tomato_model.h5")
ENV_MODEL_PATH = os.path.join(BASE_DIR, "env_model.pkl")
ENV_SCALER_PATH = os.path.join(BASE_DIR, "env_scaler.pkl")
ANOMALY_MODEL_PATH = os.path.join(BASE_DIR, "anomaly_model.pkl")

tomato_model = None
env_model = None
env_scaler = None
anomaly_model = None


def load_models():
    global tomato_model, env_model, env_scaler, anomaly_model

    if tomato_model is None:
        print("Loading tomato AI model...")
        tomato_model = tf.keras.models.load_model(TOMATO_MODEL_PATH)
        print("Tomato model loaded.")

    if env_model is None:
        env_model = joblib.load(ENV_MODEL_PATH)

    if env_scaler is None:
        env_scaler = joblib.load(ENV_SCALER_PATH)

    if anomaly_model is None:
        anomaly_model = joblib.load(ANOMALY_MODEL_PATH)


# =====================================================
# 🔹 UPDATED CLASS NAMES (3-Class Grading)
# =====================================================

class_names = ["Reject", "Ripe", "Unripe"]


# =====================================================
# 🔹 SENSOR FEATURE ENGINEERING
# =====================================================

def extract_environment_features(sensor_data):
    if not sensor_data:
        return None

    try:
        N = mean([float(d.get("nitrogen", 0)) for d in sensor_data])
        P = mean([float(d.get("phosphorus", 0)) for d in sensor_data])
        K = mean([float(d.get("potassium", 0)) for d in sensor_data])
        temperature = mean([float(d.get("temperature", 0)) for d in sensor_data])
        humidity = mean([float(d.get("humidity", 0)) for d in sensor_data])
    except ValueError:
        raise Exception("Invalid sensor data format")

    np_ratio = N / (P + 1)
    nk_ratio = N / (K + 1)

    return np.array([[N, P, K, temperature, humidity, np_ratio, nk_ratio]], dtype=np.float32)


# =====================================================
# 🔹 ENVIRONMENTAL RISK MODEL
# =====================================================

def predict_environment(sensor_data):
    load_models()

    features = extract_environment_features(sensor_data)

    if features is None:
        return 0.0, False

    features_scaled = env_scaler.transform(features)

    env_risk = float(env_model.predict(features_scaled)[0])
    env_risk = max(0.0, min(env_risk, 1.0))

    anomaly_flag = int(anomaly_model.predict(features_scaled)[0])
    anomaly_detected = anomaly_flag == -1

    return round(env_risk, 4), anomaly_detected


# =====================================================
# 🔹 IMAGE PREDICTION (FIXED SINGLE INPUT)
# =====================================================

def predict_disease(image_file):
    load_models()

    try:
        image_file.seek(0)

        img = Image.open(image_file).convert("RGB").resize((224, 224))

        img_array = np.array(img, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # ✅ FIXED: Single input model
        prediction = tomato_model.predict(img_array, verbose=0)

        prediction = np.array(prediction)

        if prediction.ndim > 1:
            prediction = prediction[0]

        disease_probability = float(np.max(prediction))
        disease_index = int(np.argmax(prediction))

        if disease_index >= len(class_names):
            raise Exception("Model output size mismatch")

        disease_class = class_names[disease_index]

        return disease_class, round(disease_probability, 4)

    except Exception as e:
        raise Exception(f"Image prediction failed: {str(e)}")


# =====================================================
# 🔹 HYBRID FUSION LOGIC
# =====================================================

def calculate_health_score(disease_prob, env_risk, anomaly_detected):

    anomaly_penalty = 0.2 if anomaly_detected else 0.0

    health_score = 1 - (
        0.6 * disease_prob +
        0.3 * env_risk +
        anomaly_penalty
    )

    health_score = max(0.0, min(health_score, 1.0))

    return round(health_score, 4)


# =====================================================
# 🔥 MAIN AI ENTRY
# =====================================================

def run_ai_analysis(sensor_data, image_file):

    if not sensor_data:
        raise Exception("Sensor data required")

    # Environmental analysis
    env_risk, anomaly_detected = predict_environment(sensor_data)

    # Tomato grading prediction
    disease_class, disease_probability = predict_disease(image_file)

    health_score = calculate_health_score(
        disease_probability,
        env_risk,
        anomaly_detected
    )

    return {
        "environmental_risk": env_risk,
        "disease_probability": disease_probability,
        "health_score": health_score,
        "anomaly_detected": anomaly_detected,
        "disease_class": disease_class
    }


# =====================================================
# 🔹 IPFS METADATA BUILDER
# =====================================================

def generate_metadata(batch, ai_result):

    metadata = {
        "batch_id": str(batch.batch_id),
        "farm_id": str(getattr(batch, "farm_id", "")),
        "timestamp": datetime.utcnow().isoformat(),
        "ai_analysis": {
            "grade": str(ai_result.get("disease_class")),
            "confidence": float(ai_result.get("disease_probability", 0)),
            "environmental_risk": float(ai_result.get("environmental_risk", 0)),
            "health_score": float(ai_result.get("health_score", 0)),
            "anomaly_detected": bool(ai_result.get("anomaly_detected", False))
        }
    }

    return metadata