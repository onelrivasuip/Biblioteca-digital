from database.conexion import obtener_conexion


class MultaDAO:
    """Gestiona las multas de la biblioteca."""

    @staticmethod
    def listar():
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    m.id,
                    m.dias_atraso,
                    m.monto,
                    m.pagada,
                    m.fecha_generacion,
                    p.id AS prestamo_id
                FROM multas m
                INNER JOIN prestamos p
                    ON m.prestamo_id = p.id
                ORDER BY m.id DESC
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def crear(
        prestamo_id,
        dias_atraso,
        monto,
    ):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO multas
                (
                    prestamo_id,
                    dias_atraso,
                    monto
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    prestamo_id,
                    dias_atraso,
                    monto,
                ),
            )

            conexion.commit()

            return cursor.lastrowid

        except Exception:
            conexion.rollback()
            raise

        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def marcar_pagada(multa_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                UPDATE multas
                SET pagada = TRUE
                WHERE id = %s
                """,
                (multa_id,),
            )

            conexion.commit()

            return cursor.rowcount

        except Exception:
            conexion.rollback()
            raise

        finally:
            cursor.close()
            conexion.close()