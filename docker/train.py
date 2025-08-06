import sys
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

# Accept path from command line
csv_path = sys.argv[1]

df = pd.read_csv(csv_path)
X = df.iloc[:, :-1]
Y = df.iloc[:, -1]

model = LinearRegression()
model.fit(X, Y)

# Save model
output_dir = "/app/models"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "model.pkl")
joblib.dump(model, output_path)

if os.path.exists(output_path):
    print(f"✅ Model trained and saved as: {output_path}")
else:
    print("❌ Model not saved!")