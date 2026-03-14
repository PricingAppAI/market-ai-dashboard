import streamlit as st

st.set_page_config(page_title="Pago PRO", page_icon=" ")

st.title(" Activar suscripción PRO")

st.write("Estás a un paso de activar tu plan PRO.")

st.markdown("---")

st.subheader("Plan PRO")

st.write(" Simulaciones ilimitadas")
st.write(" Análisis avanzado de precios")
st.write(" Dashboard empresarial")

st.markdown("### Precio: **$19.999 / mes**")

if st.button("Simular pago PRO"):

    from database.db import activar_pro

    if "user_email" in st.session_state:

        activar_pro(st.session_state.user_email)

        st.session_state.usuario_pro = True

        st.success("Pago realizado. Ahora eres usuario PRO.")

    else:

        st.error("Debes iniciar sesión primero.")
