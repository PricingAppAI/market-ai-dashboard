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

st.link_button(
    "Comprar Plan PRO",
    "https://pricingmarketai.lemonsqueezy.com/checkout/buy/047578b8-169b-46c0-8e58-bc295f959d7e"
)
