import pandas as pd
from sklearn.linear_model import LinearRegression

def train_demand_model(df):

    X = df[["precio"]]
    y = df["unidades"]

    model = LinearRegression()
    model.fit(X, y)

    return model