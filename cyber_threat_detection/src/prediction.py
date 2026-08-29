from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

# prediction.py is located inside:
# cyber_threat_detection/src/
#
# The trained models are currently located inside:
# cyber_threat_detection/notebooks/models/

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "models"
    / "final_random_forest.pkl"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "models"
    / "model_config.pkl"
)


# ---------------------------------------------------------
# Model loading
# ---------------------------------------------------------

def load_model():
    """
    Load the trained Random Forest model and configuration.

    Returns
    -------
    model : RandomForestClassifier
        Trained Random Forest model.

    config : dict
        Model configuration containing the threshold
        and feature ordering.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Model configuration not found: {CONFIG_PATH}"
        )

    model = joblib.load(MODEL_PATH)
    config = joblib.load(CONFIG_PATH)

    return model, config


# ---------------------------------------------------------
# Prediction
# ---------------------------------------------------------

def predict_network_flow(input_data):
    """
    Predict whether network traffic is BENIGN or ATTACK.

    Parameters
    ----------
    input_data : pandas.DataFrame
        DataFrame containing the required 68 network-flow
        features.

    Returns
    -------
    prediction : numpy.ndarray
        BENIGN or ATTACK predictions.

    attack_probability : numpy.ndarray
        Probability of ATTACK for each record.
    """

    model, config = load_model()

    features = config["features"]
    threshold = config["threshold"]

    # Validate input type.
    if not isinstance(input_data, pd.DataFrame):
        raise TypeError(
            "Input must be a pandas DataFrame."
        )

    # Validate empty input.
    if input_data.empty:
        raise ValueError(
            "Input DataFrame is empty."
        )

    # Check required features.
    missing_features = [
        feature
        for feature in features
        if feature not in input_data.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    # Select features in exactly the same order
    # used during model training.
    input_features = input_data[features].copy()

    # Check numeric values.
    non_numeric_columns = (
        input_features
        .select_dtypes(exclude=np.number)
        .columns
        .tolist()
    )

    if non_numeric_columns:
        raise ValueError(
            f"Non-numeric features found: "
            f"{non_numeric_columns}"
        )

    # Check missing values.
    if input_features.isnull().any().any():
        raise ValueError(
            "Input contains missing values."
        )

    # Check infinite values.
    if np.isinf(input_features.to_numpy()).any():
        raise ValueError(
            "Input contains infinite values."
        )

    # Generate ATTACK probability.
    attack_probability = model.predict_proba(
        input_features
    )[:, 1]

    # Apply our final operational threshold.
    prediction = np.where(
        attack_probability >= threshold,
        "ATTACK",
        "BENIGN"
    )

    return prediction, attack_probability