import streamlit as st

import streamlit as st

st.title(" Pago PRO")

st.write("Aquí ingresarás los datos de pago.")

if st.button("Simular pago"):
    st.success("Pago realizado (simulación)")

st.set_page_config(page_title="Pago PRO", page_icon=" ")

st.title(" Activar suscripción PRO")

st.write("Estás a un paso de activar tu plan PRO.")

st.markdown("---")

st.subheader("Plan PRO")

st.write(" Simulaciones ilimitadas")
st.write(" Análisis avanzado de precios")
st.write(" Dashboard empresarial")

st.markdown("### Precio: **$19.999 / mes**")

if st.button("Proceder al pago"):
    st.success("Aquí irá la integración con el sistema de pago.")
