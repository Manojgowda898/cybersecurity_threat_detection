import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import sqlite3
import json
from datetime import datetime

class ThreatDetectionModel:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []

    # ------------------- Data Loading -------------------
    def load_data(self, file_path=None):
        if file_path and os.path.exists(file_path):
            data = pd.read_csv(file_path)
        else:
            np.random.seed(42)
            n_samples = 10000
            # Generate synthetic network traffic dataset
            data = pd.DataFrame({
                'duration': np.random.exponential(2, n_samples),
                'protocol_type': np.random.choice(['tcp','udp','icmp'], n_samples),
                'service': np.random.choice(['http','ftp','smtp','ssh'], n_samples),
                'flag': np.random.choice(['SF','S0','REJ','RSTR'], n_samples),
                'src_bytes': np.random.exponential(1000, n_samples),
                'dst_bytes': np.random.exponential(1000, n_samples),
                'land': np.random.choice([0,1], n_samples, p=[0.95,0.05]),
                'wrong_fragment': np.random.poisson(0.1, n_samples),
                'urgent': np.random.poisson(0.01, n_samples),
                'num_failed_logins': np.random.poisson(0.1, n_samples),
                'logged_in': np.random.choice([0,1], n_samples, p=[0.3,0.7]),
                'root_shell': np.random.choice([0,1], n_samples, p=[0.95,0.05]),
                'su_attempted': np.random.choice([0,1], n_samples, p=[0.98,0.02]),
                'count': np.random.poisson(10, n_samples),
                'srv_count': np.random.poisson(8, n_samples),
                'serror_rate': np.random.uniform(0,1,n_samples),
                'rerror_rate': np.random.uniform(0,1,n_samples),
                'dst_host_serror_rate': np.random.uniform(0,1,n_samples)
            })
            # Assign synthetic attack types based on some conditions
            conditions = [
                (data['num_failed_logins'] > 3) | (data['root_shell']==1),
                (data['serror_rate'] > 0.5) | (data['rerror_rate'] > 0.5),
                (data['dst_host_serror_rate'] > 0.3) & (data['count'] > 20)
            ]
            data['attack_type'] = np.select(conditions, ['u2r','dos','probe'], default='normal')
        return data

    # ------------------- Preprocessing -------------------
    def preprocess_data(self, data):
        cat_cols = ['protocol_type','service','flag']
        data_proc = data.copy()
        for col in cat_cols:
            data_proc[col] = pd.Categorical(data_proc[col]).codes
        X = data_proc.drop('attack_type', axis=1)
        y = data_proc['attack_type']
        self.feature_names = X.columns.tolist()
        y_encoded = self.label_encoder.fit_transform(y)
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y_encoded

    # ------------------- Training -------------------
    def train_models(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(kernel='rbf', probability=True, random_state=42),
            'neural_network': MLPClassifier(hidden_layer_sizes=(100,50), max_iter=500, random_state=42)
        }
        results = {}
        for name, model in models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            results[name] = {
                'model': model,
                'accuracy': accuracy_score(y_test, y_pred),
                'report': classification_report(y_test, y_pred, output_dict=True)
            }
            self.models[name] = model
        return results

    # ------------------- Prediction -------------------
    def predict_threat(self, features, model_name='random_forest'):
        if model_name not in self.models:
            return None
        model = self.models[model_name]

        # Ensure feature vector matches trained features
        if len(features) != len(self.feature_names):
            raise ValueError(f"Expected {len(self.feature_names)} features, got {len(features)}")

        features_scaled = self.scaler.transform([features])
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        predicted_class = self.label_encoder.inverse_transform([prediction])[0]
        return {
            'predicted_class': predicted_class,
            'confidence': float(max(probabilities)),
            'probabilities': dict(zip(self.label_encoder.classes_, probabilities))
        }

    # ------------------- Save / Load Models -------------------
    def save_models(self, path='models_saved/'):
        os.makedirs(path, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f'{path}/{name}.pkl')
        joblib.dump(self.scaler, f'{path}/scaler.pkl')
        joblib.dump(self.label_encoder, f'{path}/label_encoder.pkl')
        joblib.dump(self.feature_names, f'{path}/feature_names.pkl')

    def load_models(self, path='models_saved/'):
        for name in ['random_forest','svm','neural_network']:
            self.models[name] = joblib.load(f'{path}/{name}.pkl')
        self.scaler = joblib.load(f'{path}/scaler.pkl')
        self.label_encoder = joblib.load(f'{path}/label_encoder.pkl')
        self.feature_names = joblib.load(f'{path}/feature_names.pkl')


# ------------------- Database Utilities -------------------
def init_database():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/threats.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            threat_type TEXT,
            confidence REAL,
            source_ip TEXT,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def store_alert(threat_type, confidence, source_ip, details):
    conn = sqlite3.connect('database/threats.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (timestamp, threat_type, confidence, source_ip, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), threat_type, confidence, source_ip, json.dumps(details)))
    conn.commit()
    conn.close()
