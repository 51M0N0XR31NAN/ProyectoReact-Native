"""API JSON de NOTVENCE, montada bajo el prefijo /api."""
from fastapi import APIRouter

from app.api import alertas, auth, categorias, productos

router = APIRouter(prefix="/api")
router.include_router(auth.router)
router.include_router(categorias.router)
router.include_router(productos.router)
router.include_router(alertas.router)
