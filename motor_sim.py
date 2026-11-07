# =====================================================================
#  SIMULACIÓN DE UN MOTOR DC SIMPLE  (Tema 9 - Electromagnetismo)
# =====================================================================
#
#  ¿Cómo funciona el motor? (3 ideas)
#    1. La corriente "i" en la bobina produce un torque:   torque = k * i
#    2. Al girar, la bobina genera un voltaje contrario:   fcem   = k * w
#    3. La constante del motor es:         k = N * B * A
#
# =====================================================================

import math
import random
import statistics
import matplotlib.pyplot as plt


# =====================================================================
# PARTE 1: DATOS DEL MOTOR  
# =====================================================================

# --- Bobina ---
vueltas = 20          # número de vueltas de alambre
radio = 0.015         # radio de la bobina en metros (0.015 = 1.5 cm)

# --- Imanes ---
campo_B = 0.045       # campo magnético en Tesla (se mide con gaussímetro)

# --- Circuito ---
resistencia = 1.0     # resistencia total en ohmios (se mide con multímetro)
voltaje = 1.5         # voltaje de la pila en voltios

# --- Mecánica ---
inercia = 3.4e-7      # inercia del rotor en kg*m^2
friccion = 1e-7       # fricción del eje en N*m*s

# --- Incertidumbres (qué tan seguro estoy de cada dato, en %) ---
error_B = 5           # el campo B puede variar ±5 %
error_R = 5           # la resistencia puede variar ±5 %
error_friccion = 20   # la fricción puede variar ±20 %


# =====================================================================
# PARTE 2: CÁLCULOS BÁSICOS  
# =====================================================================

pi = math.pi
area = pi * radio ** 2                 # área de la bobina
k = vueltas * campo_B * area           # constante del motor

# Para pasar de rad/s a vueltas por minuto (rpm) multiplicamos por este número:
a_rpm = 60 / (2 * pi)

# Velocidad final del motor sin carga (fórmula exacta):
w_final = k * voltaje / (k ** 2 + resistencia * friccion)

print("Constante del motor k =", k, "N*m/A")
print("Velocidad final (fórmula) =", round(w_final * a_rpm), "rpm")


# =====================================================================
# PARTE 3: ARRANQUE DEL MOTOR EN EL TIEMPO
# =====================================================================
# Avanzamos el tiempo en pasos pequeños de 0.001 s.
# En cada paso calculamos la corriente y cuánto aumenta la velocidad.

paso = 0.001            # tamaño del paso de tiempo (segundos)
w = 0                   # velocidad inicial: el motor está quieto

tiempos = []            # aquí guardamos los resultados para graficar
velocidades = []
corrientes = []

t = 0
while t < 8:                                          # simular 8 segundos
    corriente = (voltaje - k * w) / resistencia       # corriente en este instante
    torque = k * corriente - friccion * w             # torque neto
    w = w + (torque / inercia) * paso                 # la velocidad aumenta
    t = t + paso

    tiempos.append(t)
    velocidades.append(w * a_rpm)
    corrientes.append(corriente)

print("Corriente al arrancar:", round(corrientes[0], 2), "A")
print("Corriente a velocidad final:", round(corrientes[-1], 2), "A")

# Gráfica 1: el arranque
plt.figure(figsize=(9, 3.5))

plt.subplot(1, 2, 1)
plt.plot(tiempos, velocidades, label="simulación")
plt.axhline(w_final * a_rpm, color="black", linestyle="--", label="fórmula")
plt.xlabel("tiempo [s]")
plt.ylabel("velocidad [rpm]")
plt.title("Arranque del motor")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(tiempos, corrientes, color="red")
plt.xlabel("tiempo [s]")
plt.ylabel("corriente [A]")
plt.title("Corriente")

plt.savefig("fig1_arranque.png", bbox_inches="tight")


# =====================================================================
# PARTE 4: INCERTIDUMBRES (MÉTODO MONTE CARLO)
# =====================================================================
# Idea: no conocemos B, R y la fricción con exactitud.
# Entonces repetimos el cálculo 1000 veces, cambiando un poco esos
# valores al azar dentro de su error. Si los resultados varían poco,
# el motor es "estable". La variación es la BARRA DE ERROR.

repeticiones = 1000


def valor_al_azar(valor, error_porcentaje):
    """Devuelve el valor con una pequeña variación aleatoria."""
    return valor * (1 + random.gauss(0, error_porcentaje / 100))


random.seed(1)   # semilla fija: así siempre salen los mismos resultados


# ---------------------------------------------------------------------
# 4A. Velocidad sin carga para distintos voltajes
# ---------------------------------------------------------------------
lista_voltajes = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]   # voltajes a probar
vel_promedio = []
vel_error = []

print("\n Voltaje [V] | Velocidad [rpm] ± error")
for V in lista_voltajes:
    resultados = []
    for i in range(repeticiones):
        B_azar = valor_al_azar(campo_B, error_B)
        R_azar = valor_al_azar(resistencia, error_R)
        f_azar = valor_al_azar(friccion, error_friccion)
        k_azar = vueltas * B_azar * area

        velocidad = k_azar * V / (k_azar ** 2 + R_azar * f_azar)
        resultados.append(velocidad * a_rpm)

    promedio = statistics.mean(resultados)
    error = statistics.stdev(resultados)
    vel_promedio.append(promedio)
    vel_error.append(error)
    print("    ", V, "     |", round(promedio), "±", round(error))


# ---------------------------------------------------------------------
# 4B. Qué pasa cuando el motor lleva una carga (voltaje fijo)
# ---------------------------------------------------------------------
torque_bloqueo = k * voltaje / resistencia   # torque máximo (motor frenado)

lista_cargas = []                            # cargas de 0 hasta 80 % del máximo
for n in range(17):
    lista_cargas.append(n * 0.05 * torque_bloqueo)

carga_vel = []
carga_vel_error = []
carga_efi = []
carga_efi_error = []

for carga in lista_cargas:
    velocidades_azar = []
    eficiencias_azar = []
    for i in range(repeticiones):
        B_azar = valor_al_azar(campo_B, error_B)
        R_azar = valor_al_azar(resistencia, error_R)
        f_azar = valor_al_azar(friccion, error_friccion)
        k_azar = vueltas * B_azar * area

        velocidad = (k_azar * voltaje - R_azar * carga) / (k_azar ** 2 + R_azar * f_azar)
        corriente = (voltaje - k_azar * velocidad) / R_azar

        potencia_mecanica = carga * velocidad          # lo que entrega el motor
        potencia_electrica = voltaje * corriente       # lo que gasta la pila
        velocidades_azar.append(velocidad * a_rpm)
        eficiencias_azar.append(100 * potencia_mecanica / potencia_electrica)

    carga_vel.append(statistics.mean(velocidades_azar))
    carga_vel_error.append(statistics.stdev(velocidades_azar))
    carga_efi.append(statistics.mean(eficiencias_azar))
    carga_efi_error.append(statistics.stdev(eficiencias_azar))

print("\nEficiencia máxima:", round(max(carga_efi), 1), "%")


# =====================================================================
# PARTE 5: GRÁFICA 2 (RESULTADOS CON BARRAS DE ERROR)
# =====================================================================
# Pasamos el torque a mN*m (milinewton-metro) para que los números sean cómodos
cargas_mNm = []
for c in lista_cargas:
    cargas_mNm.append(c * 1000)

plt.figure(figsize=(12, 3.5))

plt.subplot(1, 3, 1)
plt.errorbar(lista_voltajes, vel_promedio, yerr=vel_error, fmt="o-", capsize=3)
plt.xlabel("voltaje [V]")
plt.ylabel("velocidad sin carga [rpm]")
plt.title("Velocidad vs voltaje")
plt.grid(alpha=0.3)

plt.subplot(1, 3, 2)
plt.errorbar(cargas_mNm, carga_vel, yerr=carga_vel_error, fmt="o-", capsize=3)
plt.xlabel("torque de carga [mN*m]")
plt.ylabel("velocidad [rpm]")
plt.title("Torque vs velocidad")
plt.grid(alpha=0.3)

plt.subplot(1, 3, 3)
plt.errorbar(cargas_mNm, carga_efi, yerr=carga_efi_error, fmt="o-", capsize=3)
plt.xlabel("torque de carga [mN*m]")
plt.ylabel("eficiencia [%]")
plt.title("Eficiencia")
plt.grid(alpha=0.3)

plt.savefig("fig2_resultados.png", bbox_inches="tight")
print("\nListo: se crearon fig1_arranque.png y fig2_resultados.png")