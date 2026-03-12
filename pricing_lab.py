import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Laboratorio de Mercado con IA")

# CONTROLES
st.sidebar.header("Parámetros del mercado")

n_agents = st.sidebar.slider("Número de empresas",2,10,3)
base_demand = st.sidebar.slider("Demanda base",50,300,150)
alpha = st.sidebar.slider("Elasticidad precio",0.1,5.0,1.5)
beta = st.sidebar.slider("Competencia cruzada",0.0,2.0,0.5)
iterations = st.sidebar.slider("Iteraciones",50,1000,300)

learning_rate = 0.01
epsilon = 0.5

prices = np.ones(n_agents)*15

price_history = []
revenue_history = []

def demand(prices):

    demands = []

    for i in range(len(prices)):

        own = base_demand - alpha*prices[i]

        cross = 0

        for j in range(len(prices)):
            if j!=i:
                cross += beta*prices[j]

        d = max(0,own + cross)

        demands.append(d)

    return np.array(demands)


def simulate_step(prices):

    d = demand(prices)

    revenues = prices*d

    return revenues


for t in range(iterations):

    gradients = np.zeros(n_agents)

    for i in range(n_agents):

        p_original = prices[i]

        prices[i] = p_original + epsilon
        r_plus = simulate_step(prices)[i]

        prices[i] = p_original - epsilon
        r_minus = simulate_step(prices)[i]

        gradient = (r_plus - r_minus)/(2*epsilon)

        gradients[i] = gradient

        prices[i] = p_original

    prices = prices + learning_rate*gradients

    price_history.append(prices.copy())
    revenue_history.append(simulate_step(prices))

price_history = np.array(price_history)
revenue_history = np.array(revenue_history)

# GRAFICO PRECIOS
fig1, ax1 = plt.subplots()

for i in range(n_agents):
    ax1.plot(price_history[:,i],label=f"Empresa {i+1}")

ax1.set_title("Evolución de precios")
ax1.set_xlabel("Iteraciones")
ax1.set_ylabel("Precio")
ax1.legend()

st.pyplot(fig1)

# GRAFICO INGRESOS
fig2, ax2 = plt.subplots()

for i in range(n_agents):
    ax2.plot(revenue_history[:,i],label=f"Empresa {i+1}")

ax2.set_title("Evolución de ingresos")
ax2.set_xlabel("Iteraciones")
ax2.set_ylabel("Revenue")
ax2.legend()

st.pyplot(fig2)

st.subheader("Resultados finales")

for i in range(n_agents):

    st.write(f"Empresa {i+1}")

    st.write("Precio:",round(prices[i],2))
    st.write("Revenue:",round(revenue_history[-1,i],2))