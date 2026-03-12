import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
st.set_page_config(layout="wide")

if "real_history" not in st.session_state:
    st.session_state.real_history = []

output_area = st.container()

results_container = st.container()
charts_container = st.container()

# =========================
# MODELO
# =========================

class Predictor:
    def __init__(self, n):
        self.w = np.random.randn(n)
        self.b = 0
        self.base_lr = 0.05
        self.lr = self.base_lr

    def predict(self, x):
        return float(np.dot(x, self.w) + self.b)

    def learn(self, x, y):
        pred = self.predict(x)
        err = y - pred

        # learning rate adaptativo estable
        if "error_history" in st.session_state and len(st.session_state.error_history) > 0:
          avg_error = np.mean(np.abs(st.session_state.error_history))
          self.lr = self.base_lr / (1 + avg_error * 0.01)
        else:
            self.lr = self.base_lr

        # límite seguro
        self.lr = max(0.001, min(self.lr, 0.05))

        # gradientes
        grad_w = err * x * 0.1
        grad_b = err

        # clipping para evitar explosión
        max_grad = 1.0
        grad_w = np.clip(grad_w, -max_grad, max_grad)
        grad_b = np.clip(grad_b, -max_grad, max_grad)

        # actualización
        self.w -= self.lr * grad_w
        self.b -= self.lr * grad_b

        return pred, err


class CognitiveAI:
    def __init__(self):
        self.pred = Predictor(3)
        self.lr = 0.005
    def step(self, x, real):
        pred, err = self.pred.learn(x, real)
        anomaly = abs(err) > 5
        action = 0 if err < 0 else 1
        return pred, err, anomaly, action


# =========================
# CARGA / PERSISTENCIA
# =========================

if "ai" not in st.session_state:
    if os.path.exists("memoria.pkl"):
        with open("memoria.pkl", "rb") as f:
            state = pickle.load(f)
        ai = CognitiveAI()
        ai.pred.w = state["weights"]
        ai.pred.b = state["bias"]
        st.session_state.ai = ai
    else:
        st.session_state.ai = CognitiveAI()

ai = st.session_state.ai

try:
    print(type(ai.pred.w), type(ai.pred.b))
except Exception as e:
    print("ERROR:", e)

if "error_history" not in st.session_state:
    st.session_state.error_history = []

if "pred_history" not in st.session_state:
    st.session_state.pred_history = []

if "real history" not in st.session_state:
    st.session_state.real_history = []

if "incertidumbre_history" not in st.session_state:
    st.session_state.incertidumbre_history = []

if "experience_buffer" not in st.session_state:
    st.session_state.experience_buffer = []

if "convergence_window" not in st.session_state:
    st.session_state.convergence_window = []

if "converged" not in st.session_state:
    st.session_state.converged = False

if "attention_weights" not in st.session_state:
    st.session_state.attention_weights = []

if "error_window" not in st.session_state:
    st.session_state.error_window = []

if "process" not in st.session_state:
    st.session_state.process = False

if "x_eff" not in st.session_state:
    st.session_state.x_eff = None

if "context_buffer" not in st.session_state:
    st.session_state.context_buffer = []

# ============================
# Normalización online
# ============================

if "norm_count" not in st.session_state:
    st.session_state.norm_count = 0
    st.session_state.norm_mean = 0.0
    st.session_state.norm_M2 = 0.0

# =========================
# INTERFAZ
# =========================

st.title("IA Cognitiva Integral")

# ===== SESSION STATE INIT =====
if "context_buffer" not in st.session_state:
    st.session_state.context_buffer = []

if "attention_weights" not in st.session_state:
    st.session_state.attention_weights = []

if "beta" not in st.session_state:
    st.session_state.beta = 1.5

if "error_window" not in st.session_state:
    st.session_state.error_window = []

if "converged" not in st.session_state:
    st.session_state.converged = False

if "training" not in st.session_state:
    st.session_state.training_phase = False

if "exploration_rate" not in st.session_state:
    st.session_state.exploration_rate = 0.3

if "uncertainty_history" not in st.session_state:
    st.session_state.uncertainty_history = []

# === CONTENEDORES ESTABLES (crear una sola vez) ===
curiosity_box = st.empty()
error_box = st.empty()
lr_box = st.empty()
status_box = st.empty()
chart_box = st.empty()

e1 = st.slider("Entrada 1", -10.0, 10.0, 2.0)
e2 = st.slider("Entrada 2", -10.0, 10.0, 1.0)
e3 = st.slider("Entrada 3", -10.0, 10.0, 3.0)

real = st.number_input("Valor real", value=4.0)

x = np.array([e1, e2, e3])

#Normalización dinámica
max_val = max(abs(x).max(), 1)

x_normalized = x / max_val
real_scaled = real / max_val

# Normalización dinámica
max_val = max(abs(x).max(), 1)
x = x / max_val

# Atención básica (placeholder)
x_att = x.copy()
context_mean =np.mean(x_normalized)

# =========================
# PROCESAMIENTO
# =========================

if "processing" not in st.session_state:
    st.session_state.processing = False

result_box = st.container()

if st.button("Procesar experiencia"):
    st.session_state.training_phase = True

    alpha = 0.7
    x_eff = alpha * x_att + (1 - alpha) * context_mean

    pred, err, anomaly, action = ai.step(x_eff, real_scaled)
    st.session_state.last_result = (pred, err, anomaly, action)

  # st.session_state.context_buffer.append(x_normalized.tolist())
    st.session_state.error_history.append(err)
    st.session_state.pred_history.append(pred)
    if "real_history" not in st.session_state:
        st.session_state.real_history = []
    st.session_state.real_history.append(real_scaled)

    with result_box:
        st.subheader("Diagnóstico IA")
        st.write("Predicción:", pred)
        st.write("Error:", err)
        st.write("Anomalía:", anomaly)
        st.write("Acción:", action)
        st.write("DEBUG:", x_eff, pred, err)

if st.session_state.converged:
    st.success("Sistema estable")
else:
    st.warning("Aprendiendo...")

with output_area:
    if st.session_state.get("process", False):

        # ===== ATENCIÓN =====
        if st.session_state.attention_weights:
            weights = np.array(st.session_state.attention_weights[-1])
        else:
            weights = np.ones_like(x)

        x_att = x * weights

        # ===== CONTEXTO =====
        if len(st.session_state.context_buffer) >= 2:
            context_mean = np.mean(
                np.array(st.session_state.context_buffer),
                axis=0
            )
        else:
            st.session_state.x_eff = x_att.copy()
       
        # ---- mostrar resultado UNA sola vez ----

        MAX_HISTORY = 100

        if len(st.session_state.pred_history) > MAX_HISTORY:
            st.session_state.pred_history.pop(0)

        if len(st.session_state.error_history) > MAX_HISTORY:
            st.session_state.error_history.pop(0)

        if len(st.session_state.real_history) > MAX_HISTORY:
            st.session_state.real_history.pop(0)

    # ===== ATENCIÓN DINÁMICA =====
    if st.session_state.attention_weights:
        weights = np.array(st.session_state.attention_weights[-1])
    else:
        weights = np.ones_like(x)

    x_att = x * weights
    if len(st.session_state.context_buffer) >= 2:
        
        context_mean = np.mean(
            np.array(st.session_state.context_buffer),
            axis=0
        )
        alpha = 0.7
        st.session_state.x_eff = alpha * x + (1 - alpha) * context_mean
    else:
        st.session_state.x_eff = x.copy()

        # ===== INCERTIDUMBRE =====
        if len(st.session_state.error_window) > 5:
            incertidumbre = np.std(st.session_state.error_window)
        else:
            incertidumbre = 0
        st.write("Incertidumbre:", incertidumbre)

        st.session_state.incertidumbre_history.append(incertidumbre)

        # limitar historial
        if len(st.session_state.incertidumbre_history) > 100:
            st.session_state.incertidumbre_history.pop(0)

        # ===== APRENDIZAJE DE ATENCIÓN =====
        beta = st.session_state.beta
        if "last_result" in st.session_state:
            _, last_err, _, _ = st.session_state.last_result
            attention_update = 1 / (1 + beta * abs(last_err))
        else:
            attention_update = 1
        new_weights = attention_update * np.ones_like(x)
        st.session_state.attention_weights.append(new_weights)

    # limitar memoria
        if len(st.session_state.attention_weights) > 50:
            st.session_state.attention_weights.pop(0)

    # ===== ADAPTACIÓN DE BETA =====
    if "err" in locals():
        st.session_state.error_window.append(abs(err))

    WINDOW = 20
    if len(st.session_state.error_window) > WINDOW:
        st.session_state.error_window.pop(0)

# =====================================
# Variables seguras desde last_result
# =====================================

if "last_result" in st.session_state:
    pred, err, anom, act = st.session_state.last_result
else:
    pred = 0.0
    err = 0.0
    anom = False
    act = 0

    # ===== DETECTOR DE CONVERGENCIA =====
    if len(st.session_state.error_window) >= 10:
        recent = st.session_state.error_window[-10:]
        if np.mean(recent) < 0.05:
            st.session_state.converged = True
        else:
            st.session_state.converged = False

    if len(st.session_state.error_window) > 5:
        variability = np.std(st.session_state.error_window)

        if variability > 1:
            st.session_state.beta *= 1.05
        else:
            st.session_state.beta *= 0.98

# límites seguros
st.session_state.beta = max(0.3, min(st.session_state.beta, 3.0))

# =============================
# EXPLORACIÓN GUIADA
# =============================
if "reward_memory" in st.session_state and len(st.session_state.reward_memory) > 5:

    best = max(st.session_state.reward_memory, key=lambda t: t[1])
    best_x = best[0]

    # moverse ligeramente hacia mejor experiencia
    x_base = x + 0.2 * (best_x - x)

else:
    x_base = x

# exploración temporal (NO modificada x real)
x_input = x_base + np.random.normal(0, 0.3, size=x.shape)

pred_explore = ai.pred.predict(x_input)
err_explore = real - pred_explore
anom_explore = abs(err_explore) > 5
act_explore = 0 if err_explore < 0 else 1

import time
time.sleep(0.03)

import math
current_time = len(st.session_state.error_history)

def priority_score(item):
    x, real, priority, timestamp = item
    age = current_time - timestamp
    decay_rate = 0.02 if priority < 1 else 0.08
    time_decay = math.exp(-decay_rate * age)
    return priority * time_decay

# inicializar buffer
if "experience_buffer" not in st.session_state:
    st.session_state.experience_buffer = []

# guardar experiencia
if "last_result" in st.session_state:
    _, last_err, _, _ = st.session_state.last_result
    priority = abs(last_err)
else:
    priority = 0
timestamp = len(st.session_state.error_history)
st.session_state.experience_buffer.append((x, real, priority, timestamp))

# usar mejores experiencias pasadas
if len(st.session_state.experience_buffer) > 5:

    best = max(st.session_state.experience_buffer, key=priority_score)
    best_x, best_real, _, _ = best

    # mover ligeramente hacia mejor experiencia
    x = x + 0.1 * (best_x - x)

max_buffer = 50
if len(st.session_state.experience_buffer) > max_buffer:
    st.session_state.experience_buffer.pop(0)

# prioritized replay
if len(st.session_state.experience_buffer) >= 5:

    # ==============================
    # MEMORIA DE RECOMPENSAS
    # ==============================

    if "reward_memory" not in st.session_state:
        st.session_state.reward_memory = []

    reward = -abs(err)  # menor error = mayor recompensa

    st.session_state.reward_memory.append((x, reward))

    # limitar memoria
    if len(st.session_state.reward_memory) > 100:
        st.session_state.reward_memory.pop(0)

    # asegurar formato numérico estable
    if isinstance(pred, (int, float)) is False:
        pred = np.array(pred, dtype=float)

    # limitar tamaño historial error
    if len(st.session_state.error_history) > 200:
        st.session_state.error_history.pop(0)

    MAX_HISTORY = 120

    for key in ["error_history", "pred_history", "novelty_history", "convergence_window"]:
        if key in st.session_state and len(st.session_state[key]) > MAX_HISTORY:
            st.session_state[key] = st.session_state[key][-MAX_HISTORY:]
    import time
    time.sleep(0.03)
# =========================
# Detector de convergencia
# =========================

if "last_result" in st.session_state:
    _, last_err, _, _ = st.session_state.last_result
    st.session_state.convergence_window.append(abs(last_err))
if len(st.session_state.convergence_window) > 20:
    st.session_state.convergence_window.pop(0)

if len(st.session_state.convergence_window) >= 10:
    variance = np.var(st.session_state.convergence_window)

    if variance < 0.0005:
        st.session_state.converged = True
    else:
        st.session_state.converged = False

# =========================
# LR Adaptativo Cognitivo
# =========================

if "lr" not in st.session_state:
    st.session_state.lr = 0.05

recent_error = np.mean(st.session_state.error_history[-10:]) if len(st.session_state.error_history) >= 10 else abs(err)

if st.session_state.converged:
    st.session_state.lr *= 0.95   # refinar
elif recent_error > 1:
    st.session_state.lr *= 1.05   # explorar
else:
    st.session_state.lr *= 0.99   # estabilizar

# límites seguros
st.session_state.lr = float(np.clip(st.session_state.lr, 0.0005, 0.5))

ai.lr = st.session_state.lr

# =============================
# Regulador de tasa de aprendizaje
# =============================

if st.session_state.converged:
    ai.lr *= 0.9   # refinar precisión
else:
    ai.lr *= 1.02  # explorar más

ai.lr = max(min(ai.lr, 0.5), 0.0001)

st.session_state.pred_history.append(pred)

    # =========================
    # Cálculo de curiosidad
    # =========================

if "novelty_history" not in st.session_state:
    st.session_state.novelty_history = []

    if len(st.session_state.pred_history) >= 10:
        recent_mean = np.mean(
            np.array(st.session_state.pred_history[-10:]),
            axis=0
        )

        novelty = np.linalg.norm(pred - recent_mean)
    else:
        novelty = float(abs(err))

    st.session_state.novelty_history.append(novelty)
    curiosity_box.info(f"Curiosidad actual: {novelty:.4f}")

# ===== GRAFICO EN VIVO =====
if len(st.session_state.error_history) > 1 and len(st.session_state.novelty_history) > 1:

    min_len = min(
        len(st.session_state.error_history),
        len(st.session_state.novelty_history)
    )

    data = pd.DataFrame({
        "error": st.session_state.error_history[:min_len],
        "curiosity": st.session_state.novelty_history[:min_len],
    })

    chart_box.line_chart(data)

# ============================
# PASO 5 — Estabilizador LR
# ============================

if len(st.session_state.error_history) >= 5:

    recent_errors = st.session_state.error_history[-5:]

    mean_error = sum(recent_errors) / len(recent_errors)

    variance = sum(
        (e - mean_error) ** 2 for e in recent_errors
    ) / len(recent_errors)

    if variance > 0.5:
        ai.pred.lr *= 0.7
    elif variance < 0.01:
        ai.pred.lr *= 1.05

    ai.pred.lr = max(0.0001, min(ai.pred.lr, 0.5))

    # Guardar experiencia

sorted_buffer = sorted(
    st.session_state.experience_buffer,
    key=priority_score,
    reverse=True
)

if st.session_state.training_phase:
    for past_x, past_real, _, _ in sorted_buffer[:10]:
        ai.step(past_x, past_real)

if "lr_history" not in st.session_state:
        st.session_state.lr_history = []

st.session_state.lr_history.append(ai.pred.lr)

    # guardar estado
state = {
    "weights": ai.pred.w,
    "bias": ai.pred.b
}

with open("memoria.pkl", "wb") as f:
    pickle.dump(state, f)

st.session_state.last_real = real
st.session_state.busy = False

# =====================
# RESULTADOS
# =====================

with results_container:

    if st.session_state.get("last_result") is not None:

        pred, err, anom, act = st.session_state.last_result

        st.subheader("Resultados")

        col1, col2, col3 = st.columns(3)

        col1.metric("Predicción", round(pred,4))
        col2.metric("Error", round(err,4))
        col3.metric("Acción", act)

        error_abs = abs(err)

        if error_abs > 0.5:
            error_box.error("Error alto — requiere más entrenamiento")

        elif error_abs > 0.1:
            status_box.warning("Error moderado — modelo ajustándose")

        else:
            status_box.success("Modelo convergiendo correctamente")
        curiosity_box.info(f"Tasa de aprendizaje actual: {ai.pred.lr:.5f}")

# =========================
# Tendencia del error
# =========================

if len(st.session_state.error_history) >= 2:

    last_error = st.session_state.error_history[-1]
    prev_error = st.session_state.error_history[-2]

    delta = last_error - prev_error

    if delta < -0.001:
        status_box.success("🔻 Error disminuyendo — aprendizaje efectivo")

    elif delta > 0.001:
        error_box.error("🔺 Error aumentando — revisar LR o datos")

    else:
        curiosity_box.info("➖ Error estable")

# =========================
# Diagnóstico de convergencia
# =========================

if len(st.session_state.error_history) > 5:

    recent = st.session_state.error_history[-5:]
    trend = recent[-1] - recent[0]

    if trend < -0.001:
        status_box.success("Diagnóstico: el modelo está mejorando")
    elif abs(trend) <= 0.001:
        status_box.warning("Diagnóstico: el modelo está estancado")
    else:
        error_box.error("Diagnóstico: el modelo está empeorando")
# =========================
# Autoajuste de learning rate
# =========================

if len(st.session_state.error_history) > 5:

    recent = st.session_state.error_history[-5:]
    decay = 0.9
    weights = np.array([decay**i for i in range(len(recent))][::-1])
    weights = weights / weights.sum()

    trend = np.sum(np.diff(recent) * weights[1:])
    volatility = np.std(recent)

    # límites seguros
    min_lr = 0.0001
    max_lr = 0.5
    ai.pred.lr = max(min_lr, min(ai.pred.lr, max_lr))

    if trend < -0.001:  
        ai.pred.lr *= 0.97   # mejora → reduce paso
        curiosity_box.info("LR ajustado: reduciendo para precisión")

    elif trend > 0.001:
        ai.pred.lr *= 1.03   # empeora → aumenta paso
        curiosity_box.info("LR ajustado: aumentando para acelerar aprendizaje")

    # clamp
    ai.pred.lr = max(min_lr, min(max_lr, ai.pred.lr))

# =====================
# GRÁFICOS
# =====================

with charts_container:

    if st.session_state.get("last_result") is not None:
        pred, err, anom, act = st.session_state.last_result

        # Gráfico 1
        if len(st.session_state.error_history) > 1:
            st.subheader("Evolución del aprendizaje")
            st.line_chart(st.session_state.error_history)
        if len(st.session_state.lr_history) > 1:
            st.subheader("Evolución del Learning Rate")
            st.line_chart(st.session_state.lr_history)

        # Gráfico 2
        if len(st.session_state.pred_history) > 1:
            st.subheader("Predicción vs Valor real")

            chart_data = {
                "Predicción": st.session_state.pred_history,
                "Real": st.session_state.real_history
            }

            st.line_chart(chart_data)

# =========================
# ESTADO INTERNO
# =========================

st.divider()
st.subheader("Estado interno IA")
st.write("Pesos predictor:", ai.pred.w)
st.write("Bias:", ai.pred.b)
st.write("Memoria acumulada:", len(st.session_state.error_history))

if len(st.session_state.error_history) > 1:
    st.subheader("Evolución del Error")

    chart_data = {
        "Error absoluto": st.session_state.error_history
    }
 
    st.line_chart(chart_data)
st.session_state.training_phase = False