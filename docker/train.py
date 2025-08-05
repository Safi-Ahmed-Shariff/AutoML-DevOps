import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

#This is a dummy data
data = {
    'feature' : [1,2,3,4,5,],
    'label' : [2,4,6,8,10]
}
df = pd.DataFrame(data)

X = df[['feature']]
Y = df['label']

model = LinearRegression()
model.fit(X, Y)

output_path = 'model.pkl'
joblib.dump(model, output_path)

if os.path.exists(output_path):
    print(f"✅ Model trained and saved as: {output_path}")
else:
    print("❌ Model not saved!")