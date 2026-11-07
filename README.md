# Simulación de motor DC simple (Tema 9) — Electromagnetismo, Universidad de La Salle

Simulación del motor DC de Rimstar (fuerza sobre conductores en campo magnético, F = I L × B).

## Ejecución
```bash
pip install -r requirements.txt
python motor_sim.py        # genera la carpeta results/
```
Semilla fija (`SEED = 2026`): los resultados son reproducibles.

## Modelo
1. **Campo B**: Biot-Savart numérico de dos imanes cilíndricos (corriente superficial K = Br/μ0), validado contra la expresión analítica sobre el eje.
2. **Constante del motor**: k = (2/π) N Φ0, con Φ0 el flujo por vuelta (conmutador ideal). kt = ke = k.
3. **Dinámica**: L di/dt = V − Ri − kω ; J dω/dt = k i − bω − τ_carga (`solve_ivp`, Radau).
4. **Estado estacionario**: ω = (kV − Rτ)/(k² + Rb).
5. **Incertidumbres**: Monte Carlo (400 muestras) sobre Br, separación, radio de espira, R y b.

## Salidas (`results/`)
`fig1_campo.png`, `fig2_transitorio.png`, `fig3_omega_vs_V.png`, `fig4_carga.png`, `tabla_omega_vs_V.csv`, `resumen.json`.

## Parámetros
Los valores de `Params` son supuestos. Reemplazar por las mediciones reales del montaje
(R con multímetro, dimensiones con calibrador, Br de la ficha del imán, etc.).
