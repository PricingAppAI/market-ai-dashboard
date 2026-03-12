import streamlit as st

st.set_page_config(
    page_title="Market AI",
    page_icon="📈",
    layout="wide"
)

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import re
import bcrypt
import sqlite3
import database.db as db
import io
import time

from database.db import init_simulations_table
from database.db import create_user
from database.db import get_user_simulations
from database.db import save_simulation
from sklearn.linear_model import LinearRegression

init_simulations_table()

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        email TEXT PRIMARY KEY,
        plan TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        price REAL,
        demand REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

def save_user(email, password_hash):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )

        conn.commit()
        success = True

    except sqlite3.IntegrityError:
        success = False

    conn.close()

    return success

def save_simulation(email, precio, demanda, ingresos):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO simulations (email, precio, demanda, ingresos)
        VALUES (?, ?, ?, ?)
        """,
        (email, precio, demanda, ingresos)
    )

    conn.commit()
    conn.close()

def get_simulations(user_email):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT precio, demanda, ingresos
        FROM simulations
        WHERE email = ?
        """,
        (user_email,)
    )

    data = cursor.fetchall()
    conn.close()

    return data

def get_user(email):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email, password_hash FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    return user

def is_pro_user(email):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT plan FROM subscriptions WHERE email=?",
        (email,)
    )

    result = cursor.fetchone()

    conn.close()

    if result and result[0] == "pro":
        return True

    return False

def get_total_users():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_total_pro_users():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM subscriptions WHERE plan='pro'"
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total

def password_strength(password):

    score = 0

    if len(password) >= 8:
        score += 1

    if re.search(r"[A-Z]", password):
       score += 1

    if re.search(r"[0-9]", password):
       score += 1

    if re.search(r"[!@#$%^&*(),.?\":{}|<>_]", password):
       score += 1

    return score

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

st.markdown(
    """
    <style>

    .feature-card {
        background-color: #1e1e1e;
        padding: 30px;
        border-radius: 14px;
        border: 1px solid #333;
        text-align: center;
        height: 220px;

        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .feature-card h3 {
        margin-bottom: 10px;
        font-size: 22px;
    }

    .feature-card p {
        font-size: 15px;
        color: #cccccc;
    }

    </style>
    """,
    unsafe_allow_html=True
)

from auth.login import login_user
from auth.register import register_user
from database.db import create_users_table
from auth.email_verification import send_verification_code
from auth.password_reset import update_password
from models.demand_model import train_demand_model

# Crear tabla de usuarios si no existe
create_users_table()

# -----------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------

st.set_page_config(
   page_title="Market AI",
   layout="wide"
)

# Estado de sesión

if "logged_in" not in st.session_state:
   st.session_state.logged_in = False

if "user_email" not in st.session_state:
   st.session_state.user_email = None

if "verification_code" not in st.session_state:
    st.session_state.verification_code = None

if "pending_email" not in st.session_state:
    st.session_state.pending_email = None

if "pending_password" not in st.session_state:
    st.session_state.pending_password = None

if "reset_email" not in st.session_state:
    st.session_state.reset_email = None

if "reset_code" not in st.session_state:
    st.session_state.reset_code = None

if "show_register" not in st.session_state:
   st.session_state.show_register = False

if "show_reset" not in st.session_state:
    st.session_state.show_reset = False

# -----------------------------
# LANDING PAGE
# -----------------------------

if not st.session_state.logged_in:
    st.markdown(
        "<h1 style='text-align:center;'>IA que encuentra el precio óptimo para maximizar tus ingresos</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
    """
    <h3 style="text-align:center;">
    Optimiza tus ingresos con inteligencia artificial
    </h3>

    <p style="text-align:center; max-width:800px; margin:auto;">
    Nuestra plataforma analiza datos de ventas y simula cómo cambia la demanda según el precio.
    Con esta herramienta puedes descubrir <b>qué precio maximiza tus ingresos</b> antes de aplicarlo en el mercado.
    </p>
    """,
    unsafe_allow_html=True
    )

    st.markdown(
    "<h2 style='text-align:center;'>¿Qué puedes hacer?</h2>",
    unsafe_allow_html=True
    )

    colA, colB, colC, colD = st.columns(4)

    with colA:
        st.markdown(
            """
            <div class="feature-card">
            <h3> Analizar ventas</h3>
            <p>Estudia datos históricos para entender cómo se comporta tu mercado.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colB:
        st.markdown(
            """
            <div class="feature-card">
            <h3> Simular precios</h3>
            <p>Simula diferentes precios y observa cómo cambia la demanda.</p>
            </div>
            """,
            unsafe_allow_html=True
         )

    with colC:
        st.markdown(
            """
            <div class="feature-card">
            <h3> Precio óptimo</h3>
            <p>La IA encuentra automáticamente el precio que maximiza ingresos.</p>
            </div>
            """,
            unsafe_allow_html=True
         )

    with colD:
        st.markdown(
            """
            <div class="feature-card">
            <h3> Maximizar ingresos</h3>
            <p>Aplica estrategias de pricing inteligentes para aumentar ganancias.</p>
            </div>
            """,
            unsafe_allow_html=True
         )

    st.markdown(
    "<h2 style='text-align:center;'>Empieza ahora</h2>",
    unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    # -------------------------
    # REGISTRO
    # -------------------------

    with col1:

        st.markdown("### Crear cuenta")

        if st.button("Crear cuenta", type="primary"):
            st.session_state.show_register = True


        if st.session_state.show_register:

            new_email = st.text_input("Correo electrónico", key="register_email")

            new_password = st.text_input(
                "Contraseña",
                type="default" if st.session_state.get("show_password", False) else "password",
                key="register_password"
            )

            # 👇 MEDIDOR DE FUERZA DE CONTRASEÑA
            if new_password:

                strength = password_strength(new_password)

                if strength <= 1:
                    st.progress(25)
                    st.error("Contraseña débil")

                elif strength == 2:
                    st.progress(50)
                    st.warning("Contraseña media")

                elif strength == 3:
                    st.progress(75)
                    st.info("Contraseña buena")

                else:
                    st.progress(100)
                    st.success("Contraseña fuerte")

            show_password = st.checkbox("Mostrar contraseña")

            st.caption("🔒 Requisitos: mínimo 8 caracteres, una mayúscula y un carácter especial")

            confirm_password = st.text_input(
                "Confirmar contraseña",
                type="default" if st.session_state.get("show_password", False) else "password",
                key="confirm_password"
            )

            email_regex = r"[^@]+@[^@]+\.[^@]+"
            password_regex = r"^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$"

            if st.button("Enviar registro"):

                if new_email == "" or new_password == "" or confirm_password == "":
                    st.error("Debes completar todos los campos")

                elif not re.match(email_regex, new_email):
                    st.error("Ingresa un correo electrónico válido")

                elif not re.match(password_regex, new_password):
                    st.error("La contraseña debe tener mínimo 8 caracteres, una mayúscula y un caracter especial")

                elif new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")

                else:
                    code = send_verification_code(new_email)

                    st.session_state.verification_code = code
                    st.session_state.verification_sent_time = time.time()
                    st.session_state.pending_email = new_email
 
                    hashed_password = hash_password(new_password)
                    st.session_state.pending_password = hashed_password

                    st.success("Se envió un código de verificación a tu correo")

        if st.session_state.verification_code:

            user_code = st.text_input("Introduce el código que recibiste por email")

            if "verification_sent_time" in st.session_state:
                segundos_pasados = time.time() - st.session_state.verification_sent_time
                espera = 30
                if segundos_pasados < espera:
                    restante = int(espera - segundos_pasados)
                    st.info(f"Puedes reenviar el código en {restante} segundos")
                else:
                    if st.button("Reenviar código de verificación"):
                        new_code = send_verification_code(st.session_state.pending_email)
                        st.session_state.verification_code = new_code
                        st.session_state.verification_sent_time = time.time()
                        st.success("Nuevo código enviado a tu correo")

            if st.button("Verificar código"):

                if user_code == st.session_state.verification_code:

                    success = save_user(
                        st.session_state.pending_email,
                        st.session_state.pending_password
                    )

                    if success:

                        st.success("Cuenta verificada y creada")

                        st.session_state.verification_code = None

                        st.session_state.logged_in = True
                        st.session_state.user_email = email

                        st.rerun()

                    else:

                        st.error("El correo ya está registrado")

                else:

                    st.error("Código incorrecto")

    # -------------------------
    # LOGIN
    # -------------------------

    with col2:
     
        left_space, login_center, right_space = st.columns([1,4,1])

        with login_center:

            st.markdown("### Iniciar sesión")

            email = st.text_input("Correo electrónico", key="login_email")

            password = st.text_input(
                "Contraseña",
                type="password",
                key="login_password"
            )

            login_col, reset_col = st.columns(2)

        with login_col:

            if st.button("Ingresar", type="primary"):

                result = login_user(email, password)

                if result:

                    st.session_state.logged_in = True
                    st.session_state.user_email = email

                    st.rerun()

                else:

                    st.error("Credenciales incorrectas")

        with reset_col:

            if st.button("Olvidé mi contraseña"):
                st.session_state.show_reset = True

    if st.session_state.show_reset:

        email_reset = st.text_input(
            "Introduce tu correo para recuperar la contraseña"
        )

        if st.button("Enviar código de recuperación"):

            code = send_verification_code(email_reset)

            st.session_state.reset_email = email_reset
            st.session_state.reset_code = code

            st.success("Código enviado a tu correo")

            st.stop()

# -----------------------------
# APP (SOLO USUARIOS LOGUEADOS)
# -----------------------------

if st.session_state.logged_in:

    st.sidebar.title("Market AI")
    st.sidebar.caption("AI Pricing Platform")

    st.sidebar.write(f"Usuario: {st.session_state.user_email}")

if st.session_state.get("logged_in", False):

    if st.sidebar.button("Cerrar sesión"):

        st.session_state.logged_in = False
        st.session_state.user_email = None

        st.rerun()

    menu = st.sidebar.radio(
        "Navegación",
        [
            "Dashboard",
            "Análisis de mercado",
            "Análisis de precios",
            "Simulador de demanda",
            "History",
            "Configuración"
        ]
    )

    if menu == "Dashboard":
 
        st.title("Market AI Dashboard")

        simulaciones = db.get_user_simulations(st.session_state.user_email)

        if simulaciones:

            df_hist = pd.DataFrame(
                simulaciones,
                columns=["precio", "demanda", "ingresos"]
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Simulaciones",
                len(df_hist)
            )

            col2.metric(
                "Precio promedio",
                round(df_hist["precio"].mean(),2)
            )

            col3.metric(
                "Demanda promedio",
                round(df_hist["demanda"].mean(),2)
            )

            col4.metric(
                "Ingreso promedio",
                round(df_hist["ingresos"].mean(),2)
            )

            st.markdown("---")
            st.subheader("Historial de ingresos")

            fig_hist = go.Figure()

            fig_hist.add_trace(
                go.Scatter(
                    x=list(range(len(df_hist))),
                    y=df_hist["ingresos"],
                    mode="lines+markers",
                    name="Ingresos"
                )
            )

            fig_hist.update_layout(
                xaxis_title="Simulación",
                yaxis_title="Ingresos",
                template="plotly_dark"
            )

            st.plotly_chart(fig_hist)

        else:
            st.info("Aún no tienes simulaciones guardadas.")

        st.markdown(
        """
        Optimiza precios con inteligencia artificial y maximiza ingresos.
        """
        )

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        col1.metric("Simulaciones realizadas", "0")
        col2.metric("Precio promedio", "$0")
        col3.metric("Demanda promedio", "0")

        st.markdown("---")
        st.subheader("Simulación de demanda")

        import numpy as np
        import pandas as pd

        precio = np.linspace(1, 100, 100)
        demanda = 120 - precio

        df_demo = pd.DataFrame({
            "Precio": precio,
            "Demanda": demanda
        })

        st.line_chart(df_demo.set_index("Precio"))
         
        st.title("Dashboard")
        st.write("Bienvenido al panel de control de Market AI.")

        st.divider()

        st.subheader("Resumen rápido")

        simulaciones = get_simulations(st.session_state.user_email)

        if simulaciones:

            total_simulaciones = len(simulaciones)

            precios = [s[0] for s in simulaciones]
            demandas = [s[1] for s in simulaciones]

            precio_promedio = sum(precios) / total_simulaciones
            demanda_promedio = sum(demandas) / total_simulaciones

            col1, col2, col3 = st.columns(3)

            col1.metric("Simulaciones realizadas", total_simulaciones)
            col2.metric("Precio promedio", round(precio_promedio, 2))
            col3.metric("Demanda promedio", round(demanda_promedio, 2))

            st.markdown("---")
            st.subheader("Histórico de simulaciones")

            df_hist = pd.DataFrame(
                simulaciones,
                columns=["Precio", "Demanda", "Fecha"]
            )

            st.line_chart(
                df_hist,
                x="Precio",
                y="Demanda"
            )

        else:

            st.info("Aún no has realizado simulaciones.")

    elif menu == "Análisis de mercado":

        st.title("Análisis de mercado")

        st.write("Explora cómo interactúan precio, demanda e ingresos.")

        st.markdown("---")

        base_demand = 200
        elasticidad = 1.5

        precios = np.linspace(1,100,100)

        demandas = base_demand - elasticidad * precios

        ingresos = precios * demandas

        df_market = pd.DataFrame({
             "Precio": precios,
             "Demanda": demandas,
             "Ingresos": ingresos
        })

        st.subheader("Curva de demanda")

        st.line_chart(
            df_market,
            x="Precio",
            y="Demanda"
        )

        st.markdown("---")

        st.subheader("Curva de ingresos")

        st.line_chart(
            df_market,
            x="Precio",
            y="Ingresos"
        )

        precio_optimo = precios[np.argmax(ingresos)]
        ingreso_max = max(ingresos)

        st.markdown("---")

        st.subheader("Precio óptimo estimado")

        st.success(f"Precio recomendado: {round(precio_optimo,2)}")

        st.write(f"Ingreso máximo estimado: {round(ingreso_max,2)}")

        st.markdown("---")
        st.subheader("Elasticidad del mercado")

        elasticidad_media = abs(elasticidad)

        if elasticidad_media < 1:
            st.success("Mercado poco sensible al precio (demanda inelástica)")

        elif elasticidad_media == 1:
            st.warning("Mercado con elasticidad unitaria")

        else:
            st.error("Mercado altamente sensible al precio (demanda elástica)")

        st.write(f"Elasticidad estimada: {round(elasticidad_media,2)}")

        st.markdown("---")
        st.subheader("Predicción de ingresos futuros")

        precio_futuro = st.slider(
            "Selecciona un precio futuro",
            min_value=1,
            max_value=100,
            value=int(precio_optimo)
        )

        demanda_futura = base_demand - elasticidad * precio_futuro
        ingresos_futuros = precio_futuro * demanda_futura

        st.write(f"Demanda estimada: {round(demanda_futura,2)}")
        st.success(f"Ingresos estimados: {round(ingresos_futuros,2)}")

    elif menu == "Simulador de demanda":

        st.title("Simulador de demanda")
        
        if "user_email" in st.session_state and st.session_state.user_email == "nelsonrivero162@gmail.com":

            st.markdown("---")
            st.subheader("📊 Panel de negocio")

            total_users = get_total_users()
            total_pro = get_total_pro_users()

            st.write(f"Usuarios registrados: {total_users}")
            st.write(f"Usuarios Pro: {total_pro}")

            ingresos_estimados = total_pro * 20000
            st.write(f"Ingresos estimados mensuales: ARS {ingresos_estimados}")

            st.write("Simula diferentes precios y observa cómo cambia la demanda.")

            st.markdown("---")

            st.subheader("Entrenar modelo con datos reales")

            uploaded_file = st.file_uploader(
                "Sube un CSV con columnas: precio, ventas",
                type=["csv"]
            )

            if uploaded_file is not None:

                df_data = pd.read_csv(uploaded_file)

                if "precio" not in df_data.columns or "unidades" not in df_data.columns:
                    st.error("El CSV debe tener columnas: precio y unidades")
                    st.stop()

                st.write("Datos cargados:")
                st.dataframe(df_data)

                X = df_data[["precio"]]
                y = df_data["unidades"]

                model = LinearRegression()
                model.fit(X, y)

                base_demand = model.intercept_
                elasticidad = -model.coef_[0]

                st.success("Modelo de demanda entrenado correctamente")

                elasticidad = model.coef_[0]

                st.write(f"Elasticidad estimada del precio: {round(elasticidad,3)}")

                st.markdown("---")
                st.subheader("Curva de demanda aprendida por el modelo")

                precios_modelo = np.linspace(
                    df_data["precio"].min(),
                    df_data["precio"].max(),
                    100
                )

                demandas_modelo = model.predict(precios_modelo.reshape(-1,1))

                df_model = pd.DataFrame({
                    "Precio": precios_modelo,
                    "Demanda estimada": demandas_modelo
                })

                st.line_chart(
                    df_model,
                    x="Precio",
                    y="Demanda estimada"
                )

                st.markdown("---")
                st.subheader("Precio óptimo según el modelo")

                # generar muchos precios posibles
                precios_test = np.linspace(
                    df_data["precio"].min(),
                    df_data["precio"].max(),
                    200
                )

                # predecir demanda para cada precio
                demandas_pred = model.predict(precios_test.reshape(-1,1))

                # calcular ingresos
                ingresos_pred = precios_test * demandas_pred

                # encontrar el máximo
                idx_max = np.argmax(ingresos_pred)

                precio_optimo_modelo = precios_test[idx_max]
                ingreso_max_modelo = ingresos_pred[idx_max]

                st.success(f"Precio recomendado: {round(precio_optimo_modelo,2)}")
                st.write(f"Ingreso máximo estimado: {round(ingreso_max_modelo,2)}")

                st.markdown("---")
                st.subheader("Superficie 3D de ingresos")

                precios_3d = np.linspace(1,100,50)
                demandas_3d = np.linspace(0, base_demand,50)

                X, Y = np.meshgrid(precios_3d, demandas_3d)

                Z = X * Y

                fig = go.Figure(data=[go.Surface(
                    x=X,
                    y=Y,
                    z=Z
                )])

                fig.update_layout(
                    scene=dict(
                        xaxis_title="Precio",
                        yaxis_title="Demanda",
                        zaxis_title="Ingresos"
                    ),
                    height=600
                )

                st.plotly_chart(fig)

            else:

                base_demand = 200
                elasticidad = 1.5

            precio = st.slider(
                "Selecciona un precio",
                min_value=1,
                max_value=100,
                value=20
            )

            demanda = base_demand - elasticidad * precio

            ingresos = precio * demanda

            # generar rango de precios
            precios = list(range(1, 101))

            # calcular demanda para cada precio
            demandas = [base_demand - elasticidad * p for p in precios]

            # calcular ingresos para cada precio
            ingresos_lista = [p * (base_demand - elasticidad * p) for p in precios]

            df_ingresos = pd.DataFrame({
                "Precio": precios,
                "Ingresos": ingresos_lista
            })

            st.subheader("Resultado de la simulación")
            st.write(f"Precio elegido: {precio}")
            st.write(f"Demanda estimada: {demanda}")
            st.write(f"Ingresos estimados: {ingresos}")

            st.markdown("---")
            st.subheader("Ingresos según el precio")

            st.line_chart(
                df_ingresos,
                x="Precio",
                y="Ingresos"
            )

            precio_optimo = precios[ingresos_lista.index(max(ingresos_lista))]
            ingreso_max = max(ingresos_lista)

            st.markdown("---")

            st.subheader("Precio óptimo")

            st.success(f"El precio que maximiza ingresos es: {precio_optimo}")
            st.write(f"Ingreso máximo estimado: {round(ingreso_max,2)}")

            st.markdown("---")
            st.subheader("Mapa de ingresos (Precio vs Demanda)")

            precios_heat = np.linspace(1, 100, 50)
            demandas_heat = np.linspace(0, base_demand, 50)

            Z = []

            for d in demandas_heat:
                fila = []
                for p in precios_heat:
                    fila.append(p * d)
                Z.append(fila)

            df_heat = pd.DataFrame(Z)

            fig = px.imshow(
                Z,
                labels=dict(x="Precio", y="Demanda", color="Ingresos"),
                x=precios_heat,
                y=demandas_heat,
                aspect="auto"
            )

            st.plotly_chart(fig, use_container_width=True)

            # -------------------------------
            # Limite de simulaciones gratuitas
            # -------------------------------

            simulaciones = db.get_user_simulations(st.session_state.user_email)

            st.info(f"Simulaciones usadas: {len(simulaciones)} / 5")
        
            if not is_pro_user(st.session_state.user_email) and len(simulaciones) >= 5:

                st.warning("Has alcanzado el límite del plan gratuito (5 simulaciones).")

                st.markdown("### Actualiza a Plan Pro para continuar")

                st.link_button(
                    "Upgrade a Pro 🚀",
                    "https://pricingmarketai.lemonsqueezy.com/checkout/buy/047578b8-169b-46c0-8e58-bc295f959d7e"
                )

                st.stop()
        
            save_simulation(
                st.session_state.user_email,
                precio,
                demanda,
                ingresos,
            )

    elif menu == "History":

          st.title("Historial")

          simulaciones = db.get_user_simulations(st.session_state.user_email)

          if simulaciones:

              df_hist = pd.DataFrame(
                  simulaciones,
                  columns=["precio","demanda","ingresos"]
              )

              st.dataframe(df_hist)

              csv = df_hist.to_csv(index=False).encode("utf-8")

              st.download_button(
                  label="Descargar simulaciones",
                  data=csv,
                  file_name="simulaciones_market_ai.csv",
                  mime="text/csv"
              )

              excel_buffer = io.BytesIO()

              with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                  df_hist.to_excel(writer, index=False, sheet_name="Simulaciones")

              excel_data = excel_buffer.getvalue()

              st.download_button(
                  label="Descargar Excel",
                  data=excel_data,
                  file_name="simulaciones_market_ai.xlsx",
                  mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              )

          else:
              st.info("Aún no tienes simulaciones guardadas.")

    elif menu == "Configuración":

          st.title("Configuración de la cuenta")

          st.write("Aquí puedes ver y administrar la información de tu cuenta.")

          st.markdown("---")

          st.subheader("Información del usuario")

          st.write(f"Correo registrado: {st.session_state.user_email}")

          st.markdown("---")

          st.subheader("Cambiar contraseña")

          new_password = st.text_input("Nueva contraseña", type="password")
          confirm_password = st.text_input("Confirmar nueva contraseña", type="password")

          if st.button("Actualizar contraseña"):

              if new_password != confirm_password:
                  st.error("Las contraseñas no coinciden")

          elif new_password == "":
              st.error("La contraseña no puede estar vacía")

          else:
              st.success("Función de cambio de contraseña en desarrollo")

              st.sidebar.markdown("---")

              if st.sidebar.button("Cerrar sesión"):
                  st.session_state.logged_in = False
                  st.session_state.user_email = None
                  st.rerun()

          if menu == "Dashboard":

              st.title("Dashboard")

              st.write("Bienvenido al panel de control de Market AI.")

              st.markdown("""
              Desde aquí puedes acceder a todas las herramientas de optimización de precios.
              """)

    elif menu == "Análisis de precios":

        st.title("Panel de análisis de precios")

        st.markdown("### Ejemplo de optimización de precio con IA")

        precio = np.linspace(1, 100, 100)
        demanda = 120 - precio + np.random.normal(0, 3, 100)

        df_demo = pd.DataFrame({
            "Precio": precio,
            "Demanda": demanda
        })
  
        st.line_chart(df_demo.set_index("Precio"))

        st.markdown("---")

        st.markdown("## Subir datos de ventas")

        st.write("Sube un archivo CSV con las columnas **precio** y **unidades**.")

        uploaded_file = st.file_uploader("Subir archivo CSV", type=["csv"])

        if uploaded_file is not None:

            df = pd.read_csv(uploaded_file)

            st.write("Vista previa de los datos:")
            st.dataframe(df)

            if "precio" in df.columns and "unidades" in df.columns:

                model = train_demand_model(df)
      
                st.success("Modelo de demanda entrenado correctamente")

                precios = np.linspace(df["precio"].min(), df["precio"].max(), 100)

                demanda_pred = model.predict(precios.reshape(-1,1))

                revenue = precios * demanda_pred

                optimal_index = np.argmax(revenue)
  
                optimal_price = precios[optimal_index]

                st.markdown(f"### Precio óptimo estimado: **${optimal_price:.2f}**")

                chart_df = pd.DataFrame({
                    "Precio": precios,
                    "Demanda": demanda_pred
                })

                st.line_chart(chart_df.set_index("Precio"))

                st.markdown("---")
                st.subheader("Ingresos según el precio")

                chart_revenue = pd.DataFrame({
                    "Precio": precios,
                    "Ingresos": revenue
                })

                st.line_chart(chart_revenue.set_index("Precio"))

                optimal_index = np.argmax(revenue)

                optimal_price = precios[optimal_index]

                optimal_revenue = revenue[optimal_index]

                st.markdown("---")
                st.subheader("Precio óptimo recomendado")

                st.success(f"Precio recomendado por el modelo: {round(optimal_price,2)}")

                st.write(f"Ingreso máximo estimado: {round(optimal_revenue,2)}")

                st.markdown("---")
                st.subheader("Mapa de ingresos (Precio vs Demanda)")

                precios_heat = np.linspace(1, 100, 50)

                demandas_heat = np.linspace(0, max(demanda_pred), 50)

                Z = []

                for d in demandas_heat:
                    fila = []
                    for p in precios_heat:
                        fila.append(p * d)
                    Z.append(fila)
 
                df_heat = pd.DataFrame(Z)

                st.dataframe(df_heat)

                st.markdown("---")
                st.subheader("Superficie de ingresos 3D")

                X, Y = np.meshgrid(precios_heat, demandas_heat)

                Z_surface = X * Y

                fig = go.Figure(
                    data=[
                        go.Surface(
                            x=X,
                            y=Y,
                            z=Z_surface
                        )
                    ]
                )

                st.plotly_chart(fig)

                st.markdown("---")
                st.subheader("Predicción de ingresos futuros")

                precio_futuro = st.slider(
                    "Selecciona un precio futuro",
                    min_value=int(df["precio"].min()),
                    max_value=int(df["precio"].max()),
                    value=int(optimal_price)
                )

                demanda_futura = model.predict([[precio_futuro]])[0]

                ingresos_futuros = precio_futuro * demanda_futura

                st.markdown("---")
                st.subheader("Precio óptimo sugerido por IA")

                precios = np.linspace(1, 100, 200)

                ingresos_pred = []

                for p in precios:
                    d = model.predict([[p]])[0]
                    ingresos_pred.append(p * d)

                precio_optimo = precios[np.argmax(ingresos_pred)]
                ingreso_max = max(ingresos_pred)

                st.success(f"Precio óptimo sugerido: ${precio_optimo:.2f}")
                st.write(f"Ingreso máximo estimado: ${ingreso_max:.2f}")

                st.markdown("---")
                st.subheader("Curva de ingresos")

                fig_revenue = go.Figure()

                fig_revenue.add_trace(
                    go.Scatter(
                        x=precios,
                        y=ingresos_pred,
                        mode="lines",
                        name="Ingresos"
                    )
                )

                fig_revenue.add_trace(
                    go.Scatter(
                        x=[precio_optimo],
                        y=[ingreso_max],
                        mode="markers",
                        marker=dict(size=12),
                        name="Precio óptimo"
                    )
                )

                fig_revenue.update_layout(
                    xaxis_title="Precio",
                    yaxis_title="Ingresos",
                    template="plotly_dark"
                )

                st.plotly_chart(fig_revenue)

                st.markdown("---")
                st.subheader("Mapa de ingresos (Precio vs Demanda)")

                precios_heat = np.linspace(1, 100, 50)
                demandas_heat = np.linspace(1, 200, 50)

                Z = []

                for d in demandas_heat:
                    fila = []
                    for p in precios_heat:
                        fila.append(p * d)
                    Z.append(fila)

                fig_heat = go.Figure(
                    data=go.Heatmap(
                        z=Z,
                        x=precios_heat,
                        y=demandas_heat,
                        colorscale="Viridis"
                    )
                )

                fig_heat.update_layout(
                    xaxis_title="Precio",
                    yaxis_title="Demanda",
                    template="plotly_dark"
                )

                st.plotly_chart(fig_heat)

                db.save_simulation(
                    st.session_state.user_email,
                    precio_futuro,
                    demanda_futura,
                    ingresos_futuros
                )

                st.write(f"Demanda estimada: {round(demanda_futura,2)}")

                st.success(f"Ingresos estimados: {round(ingresos_futuros,2)}")

                st.markdown("---")
                st.subheader("Resumen del modelo")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Precio óptimo",
                    round(optimal_price,2)
                )

                col2.metric(
                    "Demanda estimada",
                    round(demanda_futura,2)
                )

                col3.metric(
                    "Ingreso máximo",
                    round(optimal_revenue,2)
                )

                st.markdown("---")
                st.subheader("Recomendación de precio")

                if precio_futuro < optimal_price:

                    diferencia = optimal_price - precio_futuro
                    porcentaje = (diferencia / precio_futuro) * 100

                    st.warning(
                        f"El modelo sugiere subir el precio aproximadamente {round(porcentaje,1)}%"
                    )

                elif precio_futuro > optimal_price:

                    diferencia = precio_futuro - optimal_price
                    porcentaje = (diferencia / precio_futuro) * 100

                    st.warning(
                        f"El modelo sugiere bajar el precio aproximadamente {round(porcentaje,1)}%"
                    )

                else:

                    st.success("El precio actual ya es óptimo para maximizar ingresos.")

                    st.markdown("---")
                    st.subheader("Curva de elasticidad de demanda")

                    # generar rango de precios
                    precios_curve = list(range(1, 101))

                    # calcular demanda para cada precio usando el modelo
                    demandas_curve = [base_demand - elasticidad * p for p in precios_curve]

                    df_demanda = pd.DataFrame({
                        "Precio": precios_curve,
                        "Demanda": demandas_curve
                    })

                    st.line_chart(
                        df_demanda,
                        x="Precio",
                        y="Demanda"
                    )

                    st.markdown("---")
                    st.subheader("Mapa de ingresos (Precio vs Demanda)")

                    import numpy as np

                    precios_heat = np.linspace(1, 100, 50)
                    demandas_heat = np.linspace(0, base_demand, 50)

                    Z = []

                    for d in demandas_heat:
                        fila = []
                        for p in precios_heat:
                            fila.append(p * d)
                        Z.append(fila)

                    df_heat = pd.DataFrame(Z)

                    st.dataframe(df_heat)

                    st.markdown("---")
                    st.subheader("Superficie de ingresos (visualización 3D)")

                    precios_3d = np.linspace(1, 100, 40)
                    demandas_3d = np.linspace(0, base_demand, 40)

                    X, Y = np.meshgrid(precios_3d, demandas_3d)

                    Z = X * Y

                    import plotly.graph_objects as go

                    fig = go.Figure(
                        data=[
                            go.Surface(
                                x=X,
                                y=Y,
                                z=Z
                            )
                        ]
                    )

                    fig.update_layout(
                        title="Superficie de ingresos",
                        scene=dict(
                            xaxis_title="Precio",
                            yaxis_title="Demanda",
                            zaxis_title="Ingresos"
                        )
                    )

                    st.plotly_chart(fig)

                    st.markdown("---")
                    st.subheader("Historial de simulaciones")

                    simulations = get_user_simulations(st.session_state.user_email)

                    if simulations:

                        df_hist = pd.DataFrame(
                            simulations,
                            columns=["Precio", "Demanda", "Ingresos"]
                        )

                        st.dataframe(df_hist)

                    else:

                        st.info("Aún no has realizado simulaciones.")

                st.markdown("---")
                st.subheader("Simulación de ingresos futuros")

                precio_test = st.slider(
                    "Probar un precio",
                    min_value=int(df["precio"].min()),
                    max_value=int(df["precio"].max()),
                    value=int(optimal_price)
                )

                demanda_test = model.predict([[precio_test]])[0]

                ingresos_test = precio_test * demanda_test

                st.write(f"Demanda estimada: {round(demanda_test,2)}")
                st.success(f"Ingresos estimados: {round(ingresos_test,2)}")

            else:
                st.error("El CSV debe contener columnas llamadas 'precio' y 'unidades'")

                st.markdown("---")
                st.subheader("Cargar datos de mercado")

                archivo = st.file_uploader(
                    "Sube un archivo Excel con precios y demanda",
                     type=["xlsx", "csv"]
                ) 

                if archivo is not None:

                    if archivo.name.endswith(".csv"):
                        df = pd.read_csv(archivo)
                    else:
                        df = pd.read_excel(archivo)

                    st.write("Datos cargados:")
                    st.dataframe(df)

                    # -------------------------------
                    # Calcular precio óptimo
                    # -------------------------------

                    if "precio" in df.columns and "ventas" in df.columns:

                        from sklearn.linear_model import LinearRegression
                        import numpy as np

                        X = df[["precio"]]
                        y = df["ventas"]

                        model = LinearRegression()
                        model.fit(X, y)

                        precios = np.linspace(df["precio"].min(), df["precio"].max(), 100)

                        demandas = model.predict(precios.reshape(-1,1))
                        ingresos = precios * demandas

                        idx = np.argmax(ingresos)

                        precio_optimo = precios[idx]
                        ingreso_optimo = ingresos[idx]

                        st.markdown("### Precio óptimo sugerido")
                        st.success(f"Precio óptimo: {round(precio_optimo,2)}")
                        st.write(f"Ingresos estimados: {round(ingreso_optimo,2)}")
