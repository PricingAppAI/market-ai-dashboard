import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("Superficie del mercado + trayectoria de aprendizaje")

base_demand = 150
alpha = 1.5
beta = 0.5

price_range = np.linspace(5,30,40)

X,Y = np.meshgrid(price_range,price_range)
Z = np.zeros_like(X)

def demand(price_a,price_b):
    d = base_demand - alpha*price_a + beta*price_b
    return max(0,d)

# calcular superficie
for i in range(len(price_range)):
    for j in range(len(price_range)):
        p_a = X[i,j]
        p_b = Y[i,j]
        d = demand(p_a,p_b)
        Z[i,j] = p_a*d

# simulación de aprendizaje simple
price_a = 10
price_b = 10
learning_rate = 0.01

path_x=[]
path_y=[]
path_z=[]

for step in range(60):

    d = demand(price_a,price_b)
    revenue = price_a*d

    path_x.append(price_b)
    path_y.append(price_a)
    path_z.append(revenue)

    # gradiente aproximado
    epsilon = 0.1

    d_plus = demand(price_a+epsilon,price_b)
    r_plus = (price_a+epsilon)*d_plus

    gradient = (r_plus-revenue)/epsilon

    price_a += learning_rate*gradient
    price_a = max(1,price_a)

fig = go.Figure()

fig.add_trace(go.Surface(
    x=X,
    y=Y,
    z=Z,
    colorscale="Viridis",
    opacity=0.8
))

fig.add_trace(go.Scatter3d(
    x=path_x,
    y=path_y,
    z=path_z,
    mode="lines+markers",
    line=dict(width=6,color="red"),
    marker=dict(size=4)
))

fig.update_layout(
    scene=dict(
        xaxis_title="Precio competidor",
        yaxis_title="Tu precio",
        zaxis_title="Revenue"
    )
)

st.plotly_chart(fig)