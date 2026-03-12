import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Mercado con múltiples IAs aprendiendo precios")

# CONTROLES
st.sidebar.header("Parámetros")

n_agents = st.sidebar.slider("Número de empresas",2,10,4)

base_demand = st.sidebar.slider("Demanda base",50,300,150)
alpha = st.sidebar.slider("Elasticidad precio",0.1,5.0,1.5)
beta = st.sidebar.slider("Competencia cruzada",0.0,2.0,0.5)

iterations = st.sidebar.slider("Iteraciones",200,3000,1000)

price_levels = np.linspace(5,30,25)

epsilon = 0.2
learning_rate = 0.1

# Q tables
Q = np.zeros((n_agents,len(price_levels)))

prices = np.ones(n_agents)*15

price_history=[]
revenue_history=[]

def demand(prices):

    demands=[]

    for i in range(len(prices)):

        own = base_demand - alpha*prices[i]

        cross=0

        for j in range(len(prices)):
            if j!=i:
                cross += beta*prices[j]

        d=max(0,own+cross)

        demands.append(d)

    return np.array(demands)


for t in range(iterations):

    actions=[]

    for i in range(n_agents):

        if np.random.rand()<epsilon:

            a=np.random.randint(len(price_levels))

        else:

            a=np.argmax(Q[i])

        actions.append(a)

        prices[i]=price_levels[a]

    demands=demand(prices)

    revenues=prices*demands

    for i in range(n_agents):

        a=actions[i]

        Q[i,a]=Q[i,a]+learning_rate*(revenues[i]-Q[i,a])

    price_history.append(prices.copy())
    revenue_history.append(revenues.copy())

price_history=np.array(price_history)
revenue_history=np.array(revenue_history)

# GRAFICO PRECIOS

fig,ax=plt.subplots()

for i in range(n_agents):

    ax.plot(price_history[:,i],label=f"Empresa {i+1}")

ax.set_title("Evolución de precios de las IAs")
ax.set_xlabel("Iteraciones")
ax.set_ylabel("Precio")

ax.legend()

st.pyplot(fig)

# GRAFICO REVENUES

fig2,ax2=plt.subplots()

for i in range(n_agents):

    ax2.plot(revenue_history[:,i],label=f"Empresa {i+1}")

ax2.set_title("Evolución de ingresos")
ax2.set_xlabel("Iteraciones")
ax2.set_ylabel("Revenue")

ax2.legend()

st.pyplot(fig2)

st.subheader("Resultados finales")

for i in range(n_agents):

    st.write("Empresa",i+1)

    st.write("Precio final:",round(price_history[-1,i],2))

    st.write("Revenue final:",round(revenue_history[-1,i],2))