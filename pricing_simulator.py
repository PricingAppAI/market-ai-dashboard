import numpy as np
import matplotlib.pyplot as plt

# =========================
# PARÁMETROS DEL MERCADO
# =========================

A = 100
B = 2
noise_level = 1
competitor_price = 20

C = A + 0.5 * competitor_price
D = B + 0.5
optimal_price = C / (2 * D)

# =========================
# PARÁMETROS DE LAS IAs
# =========================

price_a = 15
price_b = 15
price_c = 15
price_history_a = []
price_history_b = []
price_history_c = []

learning_rate = 0.05
epsilon = 0.5
iterations = 500

# =========================
# FUNCIÓN DE DEMANDA
# =========================

def demand(price_a, price_b, price_c):

    demand_a = A - B * price_a + 0.3 * (price_b - price_a) + 0.3 * (price_c - price_a)
    demand_b = A - B * price_b + 0.3 * (price_a - price_b) + 0.3 * (price_c - price_b)
    demand_c = A - B * price_c + 0.3 * (price_a - price_c) + 0.3 * (price_b - price_c)

    demand_a = max(0, demand_a)
    demand_b = max(0, demand_b)
    demand_c = max(0, demand_c)

    return demand_a, demand_b, demand_c

def simulate_step(price_a, price_b, price_c):

    demand_a, demand_b, demand_c = demand(price_a, price_b, price_c)

    revenue_a = price_a * demand_a
    revenue_b = price_b * demand_b
    revenue_c = price_c * demand_c

    return revenue_a, revenue_b, revenue_c

# =========================
# MOTOR DE PRICING ADAPTATIVO
# =========================

iterations = 500
price = [10.0, 12.0, 8.0]
learning_rate = 0.0005

prices = [10.0, 12.0, 8.0]

last_revenue = 0
total_ai = 0
revenues = []
cumulative_revenue_ai = []

for i in range(iterations):
    revenues_step = []

    revenue_a, revenue_b, revenue_c = simulate_step(price_a, price_b, price_c)
    
    revenues_step.append(revenue_a + revenue_b + revenue_c)

    total_revenue_step = sum(revenues_step)
    total_ai += total_revenue_step
    cumulative_revenue_ai.append(total_ai)

    epsilon = 0.5

    r_plus, _, _ = simulate_step(price_a + epsilon, price_b, price_c)
    r_minus, _, _= simulate_step(price_a - epsilon, price_b, price_c)

    gradient_a = (r_plus - r_minus) / (2 * epsilon)

    price_a += learning_rate * gradient_a
    price_a = max(0.1, price_a)

    _, r_plus, _ = simulate_step(price_a, price_b, price_c + epsilon)
    _, r_minus, _ = simulate_step(price_a, price_b, price_c - epsilon)

    gradient_b = (r_plus - r_minus) / (2 * epsilon)

    price_b += learning_rate * gradient_b
    price_b = max(0.1, price_b)

    _, _, r_plus = simulate_step(price_a, price_b, price_c + epsilon)
    _, _, r_minus = simulate_step(price_a, price_b, price_c - epsilon)

    gradient_c = (r_plus - r_minus) / (2 * epsilon)

    price_c += learning_rate * gradient_c
    price_c = max(0.1, price_c)
    
    price_history_a.append(price_a)
    price_history_b.append(price_b)
    price_history_c.append(price_c)

for j in range(len(prices)):

    p_original = prices[j]
    prices[j] = p_original + epsilon
    r_plus = 0
    for p in prices:
        _, revenue, _ = simulate_step(p, price_b, price_c)
        r_plus += revenue
 
    price[j] = p_original - epsilon
    r_minus = 0
    for p in prices:
        _, revenue, _ = simulate_step(p, price_b, price_c)

    prices[j] = p_original

    gradient = (r_plus - r_minus) / (2 * epsilon)

    prices[j] += learning_rate * gradient
    prices[j] = max(0.1, prices[j])
    prices[j] = min (50, prices[j])

# ventas reales con los precios actuales
real_revenue = 0

for p in prices:
    _, revenue, _ = simulate_step(p, price_b, price_c)
    real_revenue += revenue

cumulative_revenue_ai.append(total_ai)

# =========================
# PRECIO FIJO PARA COMPARAR
# =========================

fixed_price = 18
total_fixed = 0
cumulative_revenue_fixed = []

for i in range(iterations):
    rev_a, rev_b, rev_c = simulate_step(fixed_price, fixed_price, fixed_price)
    total_fixed += revenue

    cumulative_revenue_fixed.append(total_fixed)

# =========================
# RESULTADOS
# =========================

print("Revenue IA:", round(total_ai, 2))
print("Revenue Precio Fijo:", round(total_fixed, 2))
print("Precios finales IA:", [round(p,2) for p in prices])
print("Precio óptimo teórico:", round(optimal_price,2))

revenue_a, revenue_b, revenue_c = simulate_step(price_a, price_b, price_c)

print("Precio IA A:", round(price_a,2))
print("Precio IA B:", round(price_b,2))

print("Revenue A:", round(revenue_a,2))
print("Revenue B:", round(revenue_b,2))

# =========================
# GRÁFICOS
# =========================

plt.figure(figsize=(8,5))

plt.plot(price_history_a, label="Precio IA A")
plt.plot(price_history_b, label="Precio IA B")
plt.plot(price_history_c, label="Precio IA C")

plt.axhline(optimal_price, linestyle="--", label="Precio óptimo teórico")

plt.xlabel("Iteraciones")
plt.ylabel("Precio")
plt.title("Evolución de precios de las IAs")

plt.legend()
plt.show()

# =========================
# DETECTOR DE COLUSION
# =========================

price_gap = abs(price_a - price_b)

print("\n--- Analisis de colusion ---")

if price_gap < 0.1:
    print("Posible colusión detectada")
    print("Las IAs convergieron a precios casi idénticos")

if price_a > optimal_price * 0.8:
    print("Los precios están cerca del nivel monopolístico")