from app.products_repo import get_connection


def create_movement(
    id_producto: int,
    tipo_movimiento: str,
    cantidad_movimiento: float
):
    """Registra un movimiento de un producto en MySQL."""

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO movimiento
        (id_producto, tipo_movimiento, cantidad_movimiento)
        VALUES (%s, %s, %s)
        """,
        (
            id_producto,
            tipo_movimiento,
            cantidad_movimiento
        )
    )

    conexion.commit()

    id_movimiento = cursor.lastrowid

    cursor.close()
    conexion.close()

    return id_movimiento

def list_movements(id_casa: int):
    """Lista los movimientos de los productos de una casa."""

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            m.id_movimiento,
            p.nombre_producto,
            m.tipo_movimiento,
            m.cantidad_movimiento,
            m.fecha_movimiento
        FROM movimiento m
        INNER JOIN producto p
            ON m.id_producto = p.id_producto
        WHERE p.id_casa = %s
        ORDER BY m.fecha_movimiento DESC
        """,
        (id_casa,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conexion.close()

    return rows