"""CRUD de productos del inventario contra MySQL, usado por las páginas web."""
from app.database import get_connection
from app.store import product_status


def _codigo_to_id(codigo: str) -> int | None:
    try:
        return int(codigo.split("-", 1)[1])
    except (IndexError, ValueError):
        return None


def _id_to_codigo(id_producto: int) -> str:
    return f"NV-{id_producto:03d}"


def _row_to_product(row) -> dict:
    (id_producto, nombre, categoria, presentacion, cantidad,
     fecha_vencimiento, ubicacion) = row
    cantidad = int(cantidad)
    vence = fecha_vencimiento.isoformat() if fecha_vencimiento else None
    alertas = product_status(cantidad, vence)
    estado, estado_clase = alertas[0]
    return {
        "codigo": _id_to_codigo(id_producto),
        "nombre": nombre,
        "categoria": categoria,
        "presentacion": presentacion or "Unidad",
        "cantidad": cantidad,
        "ubicacion": ubicacion or "Sin ubicación",
        "vence": vence or "Sin fecha",
        "estado": estado,
        "estado_clase": estado_clase,
        "alertas": [{"texto": texto, "clase": clase} for texto, clase in alertas],
    }
    
_SELECT_BASE = """
    SELECT p.id_producto, p.nombre_producto, c.nombre_categoria, p.presentacion,
           p.cantidad, p.fecha_vencimiento,
           GROUP_CONCAT(u.nombre_ubicacion SEPARATOR ', ') AS ubicacion
    FROM producto p
    INNER JOIN categoria c ON c.id_categoria = p.id_categoria
    LEFT JOIN producto_ubicacion pu ON pu.id_producto = p.id_producto
    LEFT JOIN ubicacion u ON u.id_ubicacion = pu.id_ubicacion
    WHERE p.id_casa = %s
"""


def list_products(id_casa: int = 1) -> list[dict]:
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        _SELECT_BASE + " GROUP BY p.id_producto ORDER BY p.id_producto",
        (id_casa,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conexion.close()
    return [_row_to_product(row) for row in rows]


def get_product(codigo: str, id_casa: int = 1) -> dict | None:
    id_producto = _codigo_to_id(codigo)
    if id_producto is None:
        return None

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        _SELECT_BASE + " AND p.id_producto = %s GROUP BY p.id_producto",
        (id_casa, id_producto),
    )
    row = cursor.fetchone()
    cursor.close()
    conexion.close()
    return _row_to_product(row) if row else None


def _resolve_categoria_id(cursor, categoria: str) -> int | None:
    cursor.execute("SELECT id_categoria FROM categoria WHERE nombre_categoria = %s", (categoria,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def _find_or_create_ubicacion(cursor, nombre: str, id_casa: int) -> int:
    cursor.execute(
        "SELECT id_ubicacion FROM ubicacion WHERE id_casa = %s AND nombre_ubicacion = %s",
        (id_casa, nombre),
    )
    resultado = cursor.fetchone()
    if resultado:
        return resultado[0]
    cursor.execute(
        "INSERT INTO ubicacion (id_casa, nombre_ubicacion) VALUES (%s, %s)",
        (id_casa, nombre),
    )
    return cursor.lastrowid


def _estado_producto_valido(estado: str) -> str:
    return "Activo" if estado == "Activo" else "Por vencer"


def _set_ubicacion(cursor, id_producto: int, ubicacion: str, cantidad: int, id_casa: int) -> None:
    cursor.execute("DELETE FROM producto_ubicacion WHERE id_producto = %s", (id_producto,))
    ubicacion = (ubicacion or "").strip()
    if not ubicacion:
        return
    id_ubicacion = _find_or_create_ubicacion(cursor, ubicacion, id_casa)
    cursor.execute(
        "INSERT INTO producto_ubicacion (id_producto, id_ubicacion, cantidad) VALUES (%s, %s, %s)",
        (id_producto, id_ubicacion, cantidad),
    )


def create_product(data: dict, id_casa: int = 1) -> dict | None:
    """data: nombre, categoria, presentacion, cantidad, ubicacion, vence, descripcion."""
    conexion = get_connection()
    cursor = conexion.cursor()

    id_categoria = _resolve_categoria_id(cursor, data["categoria"])
    if id_categoria is None:
        cursor.close()
        conexion.close()
        return None

    estado, _ = product_status(data["cantidad"], data.get("vence"))[0]
    cursor.execute(
        """
        INSERT INTO producto
        (id_casa, id_categoria, nombre_producto, descripcion,
         presentacion, cantidad, estado_producto, fecha_vencimiento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            id_casa,
            id_categoria,
            data["nombre"],
            data.get("descripcion", ""),
            data.get("presentacion") or "Unidad",
            data["cantidad"],
            _estado_producto_valido(estado),
            data.get("vence") or None,
        ),
    )
    id_producto = cursor.lastrowid
    _set_ubicacion(cursor, id_producto, data.get("ubicacion", ""), data["cantidad"], id_casa)

    conexion.commit()
    cursor.close()
    conexion.close()
    return get_product(_id_to_codigo(id_producto), id_casa)


def update_product(codigo: str, data: dict, id_casa: int = 1) -> dict | None:
    """data: nombre, categoria, presentacion, cantidad, ubicacion, vence."""
    id_producto = _codigo_to_id(codigo)
    if id_producto is None:
        return None

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("SELECT 1 FROM producto WHERE id_producto = %s AND id_casa = %s", (id_producto, id_casa))
    if not cursor.fetchone():
        cursor.close()
        conexion.close()
        return None

    id_categoria = _resolve_categoria_id(cursor, data["categoria"])
    if id_categoria is None:
        cursor.close()
        conexion.close()
        return None

    estado, _ = product_status(data["cantidad"], data.get("vence"))[0]
    cursor.execute(
        """
        UPDATE producto
        SET id_categoria = %s, nombre_producto = %s, presentacion = %s,
            cantidad = %s, estado_producto = %s, fecha_vencimiento = %s
        WHERE id_producto = %s AND id_casa = %s
        """,
        (
            id_categoria,
            data["nombre"],
            data.get("presentacion") or "Unidad",
            data["cantidad"],
            _estado_producto_valido(estado),
            data.get("vence") or None,
            id_producto,
            id_casa,
        ),
    )
    _set_ubicacion(cursor, id_producto, data.get("ubicacion", ""), data["cantidad"], id_casa)

    conexion.commit()
    cursor.close()
    conexion.close()
    return get_product(codigo, id_casa)


def delete_product(codigo: str, id_casa: int = 1) -> bool:
    id_producto = _codigo_to_id(codigo)
    if id_producto is None:
        return False

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM producto WHERE id_producto = %s AND id_casa = %s", (id_producto, id_casa))
    conexion.commit()
    eliminado = cursor.rowcount > 0
    cursor.close()
    conexion.close()
    return eliminado
