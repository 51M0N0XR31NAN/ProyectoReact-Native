"""Endpoint de productos con alertas activas (por vencer, vencidos o stock bajo)."""
from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.schemas import ProductOut
from app.store import PRODUCTS

router = APIRouter(tags=["Alertas"])


@router.get("/alertas", response_model=list[ProductOut], summary="Lista productos con alerta activa")
def listar_alertas(user: str = Depends(get_current_user)):
    return [product for product in PRODUCTS if product["estado"] != "Activo"]
