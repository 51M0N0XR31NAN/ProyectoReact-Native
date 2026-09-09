"""Endpoints CRUD para productos del inventario."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.deps import get_current_user
from app.products_repo import (
    list_products,
    get_product,
    create_product,
    update_product,
    delete_product,
)
from app.schemas import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/productos", tags=["Productos"])


# ===================
# LISTAR PRODUCTOS
# ==================

@router.get(
    "",
    response_model=list[ProductOut],
    summary="Lista productos del inventario",
)
def listar_productos(
    categoria: str | None = None,
    estado: str | None = None,
    q: str | None = Query(
        default=None,
        description="Busca por nombre o código",
    ),
    user: str = Depends(get_current_user),
):
    productos = list_products()

    if categoria:
        productos = [
            p for p in productos
            if p["categoria"] == categoria
        ]

    if estado:
        productos = [
            p for p in productos
            if p["estado"] == estado
        ]

    if q:
        needle = q.lower()

        productos = [
            p for p in productos
            if needle in p["nombre"].lower()
            or needle in p["codigo"].lower()
        ]

    return productos


# ==========================
# OBTENER UN PRODUCTO
# =========================

@router.get(
    "/{codigo}",
    response_model=ProductOut,
    summary="Obtiene un producto por código",
)
def obtener_producto(
    codigo: str,
    user: str = Depends(get_current_user),
):
    producto = get_product(codigo)

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto '{codigo}' no encontrado.",
        )

    return producto


# =================
# CREAR PRODUCTO
# ================

@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un producto",
)
def crear_producto(
    payload: ProductCreate,
    user: str = Depends(get_current_user),
):
    producto = create_product(
        {
            "nombre": payload.nombre,
            "categoria": payload.categoria,
            "presentacion": payload.presentacion,
            "cantidad": payload.cantidad,
            "ubicacion": payload.ubicacion,
            "vence": payload.vence,
        }
    )

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría indicada no existe.",
        )

    return producto


# =====================
# ACTUALIZAR PRODUCTO
# ====================

@router.put(
    "/{codigo}",
    response_model=ProductOut,
    summary="Actualiza un producto existente",
)
def actualizar_producto(
    codigo: str,
    payload: ProductUpdate,
    user: str = Depends(get_current_user),
):
    producto = update_product(
        codigo,
        {
            "nombre": payload.nombre,
            "categoria": payload.categoria,
            "presentacion": payload.presentacion,
            "cantidad": payload.cantidad,
            "ubicacion": payload.ubicacion,
            "vence": payload.vence,
        },
    )

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto '{codigo}' no encontrado.",
        )

    return producto


# =====================
# ELIMINAR PRODUCTO
# ====================

@router.delete(
    "/{codigo}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina un producto",
)
def eliminar_producto(
    codigo: str,
    user: str = Depends(get_current_user),
):
    eliminado = delete_product(codigo)

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto '{codigo}' no encontrado.",
        )

    return None