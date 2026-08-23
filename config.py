"""
config.py

Parámetros del negocio que no dependen del entorno (a diferencia de las
credenciales de MySQL, que viven en variables de entorno / .env — ver
database/conexion.py).
"""

DIAS_PRESTAMO = 7        # días que dura un préstamo antes de la fecha límite
MULTA_POR_DIA = 0.50     # multa en dólares por cada día de atraso
