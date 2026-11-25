"""Experimentos del documento: ¿qué conclusiones cambian si cambio un supuesto?

Uso: python3 experimentos.py
"""
import contextlib
import io

import estimaciones as e

FILAS = ["Facturas al mes", "Peticiones/s en hora pico", "Cron de Gmail en una sola corrida (s)",
         "Cron de Gmail por despacho (s)", "Crecimiento de la base de datos (MB al mes)", "Archivos nuevos (GB al mes)"]


def tabla(titulo):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        e.correr()
    lineas = buf.getvalue().splitlines()
    print(f"### {titulo}\n")
    print(lineas[0]); print(lineas[1])
    for l in lineas[2:]:
        if any(l.startswith(f"| {f}") for f in FILAS):
            print(l)
    print()


base_f, base_g = e.SUPUESTOS["facturas_por_cliente_mes"], e.GMAIL_S_POR_CONEXION
tabla("Base (40 facturas por cliente, 10 s por conexión de Gmail)")
e.SUPUESTOS["facturas_por_cliente_mes"] = 120
tabla("120 facturas por cliente al mes")
e.SUPUESTOS["facturas_por_cliente_mes"] = 10
tabla("10 facturas por cliente al mes")
e.SUPUESTOS["facturas_por_cliente_mes"] = base_f
e.GMAIL_S_POR_CONEXION = 60
tabla("60 s por conexión de Gmail (en vez de 10)")
