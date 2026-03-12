import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Simulador de Pricing con IA")

st.sidebar.header("Parámetros del mercado")

base_demand = st.sidebar.slider("Demanda base", 50, 200, 120)
alpha = st.sidebar.slider("Sensibilidad al precio", 0.1, 5.0, 1.5)
beta = st.sidebar.slider("Competencia cruzada", 0.0, 2.0, 0.5)

iterations = st.sidebar.slider("Iteraciones", 50, 1000, 300)

price_a = 15.0
price_b = 15.0
price_c = 15.0

learning_rate = 0.01
epsilon = 0.5

price_history_a = []
price_history_b = []
price_history_c = []

def demand(price_a, price_b, price_c):

    demand_a = base_demand - alpha * price_a + beta * (price_b + price_c)
    demand_b = base_demand - alpha * price_b + beta * (price_a + price_c)
    demand_c = base_demand - alpha * price_c + beta * (price_a + price_b)

    return max(0,demand_a), max(0,demand_b), max(0,demand_c)

def simulate_step(price_a, price_b, price_c):

    demand_a, demand_b, demand_c = demand(price_a, price_b, price_c)

    revenue_a = price_a * demand_a
    revenue_b = price_b * demand_b
    revenue_c = price_c * demand_c

    return revenue_a, revenue_b, revenue_c

for i in range(iterations):

    r_plus, _, _ = simulate_step(price_a + epsilon, price_b, price_c)
    r_minus, _, _ = simulate_step(price_a - epsilon, price_b, price_c)

    gradient_a = (r_plus - r_minus) / (2*epsilon)
    price_a += learning_rate * gradient_a

    _, r_plus, _ = simulate_step(price_a, price_b + epsilon, price_c)
    _, r_minus, _ = simulate_step(price_a, price_b - epsilon, price_c)

    gradient_b = (r_plus - r_minus) / (2*epsilon)
    price_b += learning_rate * gradient_b

    _, _, r_plus = simulate_step(price_a, price_b, price_c + epsilon)
    _, _, r_minus = simulate_step(price_a, price_b, price_c - epsilon)

    gradient_c = (r_plus - r_minus) / (2*epsilon)
    price_c += learning_rate * gradient_c

    price_history_a.append(price_a)
    price_history_b.append(price_b)
    price_history_c.append(price_c)

fig, ax = plt.subplots()

ax.plot(price_history_a,label="IA A")
ax.plot(price_history_b,label="IA B")
ax.plot(price_history_c,label="IA C")

ax.set_xlabel("Iteraciones")
ax.set_ylabel("Precio")
ax.set_title("Evolución de precios")

ax.legend()

st.pyplot(fig)

rev_a, rev_b, rev_c = simulate_step(price_a,price_b,price_c)

st.subheader("Resultados finales")

st.write("Precio IA A:",round(price_a,2))
st.write("Precio IA B:",round(price_b,2))
st.write("Precio IA C:",round(price_c,2))

st.write("Revenue IA A:",round(rev_a,2))
st.write("Revenue IA B:",round(rev_b,2))
st.write("Revenue IA C:",round(rev_c,2))