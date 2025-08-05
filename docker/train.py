import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

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

joblib.dump(model, 'model.pkl')
print("Model trained and saved as model.pkl")