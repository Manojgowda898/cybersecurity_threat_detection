# train_models.py
from models.threat_model import ThreatDetectionModel

# Initialize the threat detector
detector = ThreatDetectionModel()

# Generate synthetic network data
print("Generating synthetic data...")
data = detector.load_data()  # uses built-in synthetic generator
X, y = detector.preprocess_data(data)

# Train models
print("Training models...")
results = detector.train_models(X, y)

# Print model accuracies
for model_name, info in results.items():
    print(f"{model_name} Accuracy: {info['accuracy']:.4f}")

# Save models to models_saved/
detector.save_models('models_saved/')
print("✅ Models trained and saved in 'models_saved/'")
