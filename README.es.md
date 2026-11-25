🇬🇧 [English](README.md) · 🇪🇸 Español

🎬 **Video (en inglés, ~9 min) que explica los cuatro proyectos del portafolio:** [verlo](https://github.com/close-cr/close-cr/blob/main/media/portfolio-walkthrough.mp4)
# Rediseño de una app contable real para crecer 100 veces

Caso de estudio de diseño de sistemas sobre **Cont Finance**, una plataforma web contable multi-despacho: qué se rompe primero si el uso crece unas 100 veces, qué cambiar y cuándo.

- 📄 **[DISENO.es.md](DISENO.es.md)**: el documento de diseño completo (requisitos, estimaciones, cuellos de botella, propuesta, plan por fases, experimentos).
- 🧮 **`estimates.py`**: el modelo de estimaciones detrás de los números (`python3 estimates.py`).
- 🔬 **`experiments.py`**: cómo cambian las conclusiones al mover un supuesto (`python3 experiments.py`).

**Hallazgo principal:** la capa web no es el cuello de botella (~9 peticiones por segundo a ×100). Lo primero que se rompe es el trabajo de Gmail en una sola corrida (≈ 3.333 s contra un límite de 300 s), el tope de cuentas de Gmail sin verificar y el tamaño de la base, y el arreglo es repartir el trabajo por despacho, con reintentos idempotentes.

Todo es estimación (los supuestos son explícitos); no se afirma ninguna medición del sistema real. Costo cero, solo Python estándar.
