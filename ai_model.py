import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load training data
with open("training_data.json", "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Preprocess
# Map categorical values to numbers
mapping = {
    "Species": {"C": 0, "P": 1, "H": 2, "S": 3, "G": 4, "K": 5},
    "Breeding Status": {
        "Ready for Breeding": 0,
        "Not Ready for Breeding": 1,
        "Cannot Breed": 2
    },
    "Lifestyle": {
        "Active and Grazing": 0,
        "Sedentary": 1,
        "Used for Labour": 2
    },
    "Health Status": {
        "Stable": 0,
        "Under Observation": 1,
        "Critical Condition": 2
    },
    "Risk": {
        "Low": 0,
        "Medium": 1,
        "High": 2
    }
}

df["Species"] = df["Species"].map(mapping["Species"])
df["Breeding Status"] = df["Breeding Status"].map(mapping["Breeding Status"])
df["Lifestyle"] = df["Lifestyle"].map(mapping["Lifestyle"])
df["Health Status"] = df["Health Status"].map(mapping["Health Status"])
df["Risk"] = df["Risk"].map(mapping["Risk"])

# Features and labels
X = df[["Species", "Age", "Breeding Status", "Lifestyle", "Health Status"]]
y = df["Risk"]

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved as model.pkl")
