"""Endpoint de productos con alertas activas (por vencer, vencidos o stock bajo)."""
from fastapi import APIRouter, Depends

from app.deps import get_current_casa
from app.products_repo import list_products
from app.schemas import ProductOut

router = APIRouter(tags=["Alertas"])


@router.get("/alertas", response_model=list[ProductOut], summary="Lista productos con alerta activa")
def listar_alertas(id_casa: int = Depends(get_current_casa)):
    productos = list_products(id_casa)
    return [product for product in productos if product["estado"] != "Activo"]
