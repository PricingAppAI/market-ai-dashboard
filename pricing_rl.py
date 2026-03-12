import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Simulador de Pricing con Reinforcement Learning")

# CONTROLES
st.sidebar.header("Parámetros")

base_demand = st.sidebar.slider("Demanda base",50,300,150)
alpha = st.sidebar.slider("Elasticidad precio",0.1,5.0,1.5)
beta = st.sidebar.slider("Competencia cruzada",0.0,2.0,0.5)

iterations = st.sidebar.slider("Iteraciones",100,2000,500)

price_levels = np.linspace(5,30,20)

# Q TABLE
Q = np.zeros(len(price_levels))

epsilon = 0.2
learning_rate = 0.1

price_history=[]
revenue_history=[]

def demand(price, competitor_price):

    d = base_demand - alpha*price + beta*competitor_price

    return max(0,d)


competitor_price=15

for t in range(iterations):

    if np.random.rand()<epsilon:

        action=np.random.randint(len(price_levels))

    else:

        action=np.argmax(Q)

    price=price_levels[action]

    d=demand(price,competitor_price)

    revenue=price*d

    Q[action]=Q[action]+learning_rate*(revenue-Q[action])

    price_history.append(price)
    revenue_history.append(revenue)

price_history=np.array(price_history)
revenue_history=np.array(revenue_history)

# GRAFICO PRECIO

fig,ax=plt.subplots()

ax.plot(price_history)

ax.set_title("Precio elegido por la IA")

ax.set_xlabel("Iteraciones")
ax.set_ylabel("Precio")

st.pyplot(fig)

# GRAFICO REVENUE

fig2,ax2=plt.subplots()

ax2.plot(revenue_history)

ax2.set_title("Revenue obtenido")

ax2.set_xlabel("Iteraciones")
ax2.set_ylabel("Revenue")

st.pyplot(fig2)

best_price=price_levels[np.argmax(Q)]

st.subheader("Resultado final")

st.write("Precio aprendido por la IA:",round(best_price,2))
st.write("Revenue esperado:",round(max(Q),2))