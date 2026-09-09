"""Endpoints de categorías y presentaciones."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user
from app.store import PRESENTATIONS

router = APIRouter(tags=["Categorías"])


@router.get("/categorias", summary="Lista las categorías disponibles")
def listar_categorias(user: str = Depends(get_current_user)):
    return {"categorias": sorted(PRESENTATIONS.keys())}


@router.get(
    "/categorias/{categoria}/presentaciones",
    summary="Presentaciones disponibles para una categoría",
)
def listar_presentaciones(categoria: str, user: str = Depends(get_current_user)):
    if categoria not in PRESENTATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría '{categoria}' no encontrada.",
        )
    return {"categoria": categoria, "presentaciones": PRESENTATIONS[categoria]}
