import streamlit as st
import pandas as pd
import sqlite3

if "user_email" not in st.session_state or st.session_state.user_email is None:
    st.warning("Debes iniciar sesión primero.")
    st.stop()

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

st.title("Historial de análisis")

cursor.execute(
    "SELECT producto, precio_actual, precio_optimo, ingresos_estimados, fecha FROM analysis_history WHERE user_email=?",
    (st.session_state.user_email,)
)

rows = cursor.fetchall()

if rows:

    history_df = pd.DataFrame(
        rows,
        columns=[
            "Producto",
            "Precio actual",
            "Precio recomendado",
            "Ingresos estimados",
            "Fecha"
        ]
    )

    st.dataframe(history_df)

else:
    st.info("Aún no tienes análisis guardados.")