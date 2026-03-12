import streamlit as st
import pandas as pd
import numpy as np

from models.demand_model import train_demand_model
    
st.title("Motor de Precios con IA")

st.subheader("Subir datos de ventas (CSV)")

uploaded_file = st.file_uploader(
    "Sube un archivo CSV con columnas: producto, precio, units_sold, coste",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

if st.button("Generar datos de ejemplo"):

    data = {
        "producto": ["A","B","C","D","E"],
        "precio": [10,12,9,15,11],
        "units_sold": [120,100,150,80,110],
        "coste": [4,5,3,6,4]
    }

    df = pd.DataFrame(data)

    if df is not None:

        model = train_demand_model(df)

        st.success("Modelo entrenado")

        st.dataframe(df)

        for index, row in df.iterrows():

            save_analysis(
                st.session_state.user_email,
                row["producto"],
                row["precio"],
                row["precio"], 
                row["precio"] * row["units_sold"]
            )

        import numpy as np
        import matplotlib.pyplot as plt

        st.subheader("Curva de demanda estimada")

        price_range = np.linspace(df["precio"].min()*0.5, df["precio"].max()*1.5, 50)

        predicted_demand = model.predict(price_range.reshape(-1,1))

        revenue = price_range * predicted_demand

        optimal_index = np.argmax(revenues)

        optimal_price = prices[optimal_index]

        optimal_revenue = revenue[optimal_index]

        fig, ax = plt.subplots()

        ax.plot(price_range, predicted_demand, label="Demanda")
        ax.plot(price_range, revenue, label="Ingresos")

        ax.set_xlabel("Precio")
        ax.set_ylabel("Valor")
        ax.legend()

        st.pyplot(fig)

        st.subheader("Precio óptimo estimado por IA")
    
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Precio óptimo", f"${optimal_price:.2f}")

        with col2:

            st.metric("Ingreso máximo estimado", f"${optimal_revenue:.2f}")