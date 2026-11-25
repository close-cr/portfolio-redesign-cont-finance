"""Estimaciones (back-of-envelope) de una app contable multi-despacho en tres escenarios de tamaño.

Todo lo que no es un dato medido es un SUPUESTO explícito (ver SUPUESTOS). Cambiar un número
y volver a correr el script actualiza las tablas del documento DISENO.md.

Uso:  python3 estimaciones.py
"""

# --- Límites de la plataforma de ejemplo y de Google (documentados por sus proveedores) ---
CRON_MAX_S = 300           # tiempo máximo por corrida de cron en la plataforma actual
GMAIL_PARALELO = 15        # conexiones de Gmail que el bot procesa en paralelo
GMAIL_S_POR_CONEXION = 10  # segundos aproximados por conexión (estimado, no medido)
POOL_POR_INSTANCIA = 5     # conexiones a la base por instancia de la app
DB_LIMITE_MB = 512         # SUPUESTO: tamaño de un plan pequeño de base de datos
GMAIL_TOPE_SIN_VERIFICAR = 100  # tope de usuarios de una app de Google sin verificar

# --- Escenarios ---
ESCENARIOS = {
    "Escenario pequeño":          dict(despachos=1,   clientes_activos=10),    # SUPUESTO: un despacho que empieza
    "Escenario medio":            dict(despachos=20,  clientes_activos=1000),  # SUPUESTO: ~50 clientes por despacho
    "Escenario de diseño (×100)": dict(despachos=100, clientes_activos=5000),  # SUPUESTO: ~100 veces el escenario pequeño en despachos
}

SUPUESTOS = dict(
    facturas_por_cliente_mes=40,   # «decenas o cientos» según las guías; se toma 40
    kb_archivo_por_factura=150,    # XML (~20 KB) + PDF (~130 KB)
    kb_base_por_factura=5,         # fila de factura + líneas + asiento contable
    usuarios_por_despacho=3,
    peticiones_por_usuario_hora=120,  # navegación normal: 2 por minuto
    horas_pico_concurrencia=0.3,   # fracción de usuarios activos a la vez en la hora pico
    factor_pico=3,                 # pico = 3 × promedio
    latencia_peticion_s=0.2,       # tiempo medio que una petición ocupa una conexión a la base (SUPUESTO)
    pct_solo_pdf=0.10,             # facturas sin XML que necesitan lectura con IA
)


def fmt(n, d=0):
    return f"{n:,.{d}f}".replace(",", " ")


def correr():
    s = SUPUESTOS
    print("| Magnitud | " + " | ".join(ESCENARIOS) + " |")
    print("|---|" + "---|" * len(ESCENARIOS))
    filas = {}
    for nombre, e in ESCENARIOS.items():
        fac = e["clientes_activos"] * s["facturas_por_cliente_mes"]
        usuarios = e["despachos"] * s["usuarios_por_despacho"]
        activos = usuarios * s["horas_pico_concurrencia"]
        rps_pico = activos * (s["peticiones_por_usuario_hora"] / 3600) * s["factor_pico"]
        bot_s = e["clientes_activos"] / GMAIL_PARALELO * GMAIL_S_POR_CONEXION  # un solo cron para todos
        bot_s_desp = (e["clientes_activos"] / e["despachos"]) / GMAIL_PARALELO * GMAIL_S_POR_CONEXION  # un despacho
        base_mb = fac * s["kb_base_por_factura"] / 1024
        arch_gb = fac * s["kb_archivo_por_factura"] / 1024 / 1024
        filas.setdefault("Clientes activos al mes", []).append(fmt(e["clientes_activos"]))
        filas.setdefault("Facturas al mes", []).append(fmt(fac))
        filas.setdefault("Facturas al día (30 días)", []).append(fmt(fac / 30))
        filas.setdefault("Usuarios totales", []).append(fmt(usuarios))
        filas.setdefault("Peticiones/s en hora pico", []).append(fmt(rps_pico, 1))
        filas.setdefault("Conexiones a la base en uso a la vez (ley de Little: peticiones/s × latencia)", []).append(fmt(rps_pico * s["latencia_peticion_s"], 1))
        filas.setdefault("Cron de Gmail en una sola corrida (s)", []).append(f"{fmt(bot_s)} ({'EXCEDE' if bot_s > CRON_MAX_S else 'cabe'} en {CRON_MAX_S} s)")
        filas.setdefault("Cron de Gmail por despacho (s)", []).append(f"{fmt(bot_s_desp)} ({'excede' if bot_s_desp > CRON_MAX_S else 'cabe'})")
        filas.setdefault("Cuentas de Gmail conectadas (≈ 1 por cliente)", []).append(f"{fmt(e['clientes_activos'])} ({'sobre' if e['clientes_activos'] > GMAIL_TOPE_SIN_VERIFICAR else 'bajo'} el tope de {GMAIL_TOPE_SIN_VERIFICAR})")
        filas.setdefault("Crecimiento de la base de datos (MB al mes)", []).append(f"{fmt(base_mb)} ({'supera' if base_mb > DB_LIMITE_MB else 'bajo'} {DB_LIMITE_MB} MB supuestos)")
        filas.setdefault("Archivos nuevos (GB al mes)", []).append(fmt(arch_gb, 1))
        filas.setdefault("Facturas que necesitan IA (solo PDF) al mes", []).append(fmt(fac * s["pct_solo_pdf"]))
    for k, v in filas.items():
        print(f"| {k} | " + " | ".join(v) + " |")


if __name__ == "__main__":
    correr()
