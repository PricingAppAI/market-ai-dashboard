import streamlit as st
import pandas as pd
import sqlite3

# Seguridad de sesión
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Debes iniciar sesión primero.")
    st.stop()

st.title("Dashboard de Pricing AI")

# Conectar base de datos
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute(
    """
    SELECT producto, precio_actual, precio_optimo, ingresos_estimados, fecha
     FROM analysis_history
    WHERE user_email=?
    """,
    (st.session_state.user_email,)
)

rows = cursor.fetchall()

if rows:

    df = pd.DataFrame(
        rows,
        columns=[
            "Producto",
            "Precio actual",
            "Precio recomendado",
            "Ingresos estimados",
            "Fecha"
        ]
    )

    # Métricas principales
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Análisis realizados",
        len(df)
    )

    col2.metric(
        "Ingresos estimados totales",
        int(df["Ingresos estimados"].sum())
    )

    col3.metric(
        "Precio promedio recomendado",
        round(df["Precio recomendado"].mean(), 2)
    )

    st.subheader("Historial de ingresos estimados")

    chart_df = df[["Fecha", "Ingresos estimados"]].copy()
    chart_df["Fecha"] = pd.to_datetime(chart_df["Fecha"])

    chart_df = chart_df.sort_values("Fecha")

    st.line_chart(
        chart_df.set_index("Fecha")
    )

    st.subheader("Productos analizados")

    st.dataframe(df)

else:

    st.info("Todavía no hay análisis para mostrar en el dashboard.")