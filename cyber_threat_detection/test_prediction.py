from src.prediction import load_model


model, config = load_model()

print("Model loaded successfully!")
print("Model type:", type(model))
print("Feature count:", len(config["features"]))
print("Threshold:", config["threshold"])