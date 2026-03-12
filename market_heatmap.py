import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Mapa de mercado de precios")

st.sidebar.header("Parámetros")

base_demand = st.sidebar.slider("Demanda base",50,300,150)
alpha = st.sidebar.slider("Elasticidad precio",0.1,5.0,1.5)
beta = st.sidebar.slider("Competencia cruzada",0.0,2.0,0.5)

price_range = np.linspace(5,30,50)

heatmap = np.zeros((len(price_range),len(price_range)))

def demand(price_a,price_b):

    d = base_demand - alpha*price_a + beta*price_b

    return max(0,d)

for i,p_a in enumerate(price_range):

    for j,p_b in enumerate(price_range):

        d = demand(p_a,p_b)

        revenue = p_a*d

        heatmap[i,j] = revenue

fig,ax = plt.subplots()

c = ax.imshow(
    heatmap,
    origin="lower",
    extent=[5,30,5,30],
    aspect="auto"
)

ax.set_xlabel("Precio competidor")
ax.set_ylabel("Tu precio")

ax.set_title("Mapa de revenue")

fig.colorbar(c)

st.pyplot(fig)