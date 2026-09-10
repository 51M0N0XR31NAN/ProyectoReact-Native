"""Esquemas Pydantic para la API JSON de NOTVENCE."""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Categoria = Literal["Alimentos", "Bebidas", "Aseo", "Medicamentos", "Otros"]
EstadoClase = Literal["success", "warning", "danger"]


class ProductBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    categoria: Categoria
    presentacion: str = Field(min_length=1, max_length=60)
    cantidad: int = Field(ge=0)
    ubicacion: str = Field(min_length=1, max_length=80)
    vence: Optional[str] = Field(default=None, description="Fecha de vencimiento en formato YYYY-MM-DD")

    @field_validator("vence")
    @classmethod
    def validar_fecha(cls, value: str | None) -> str | None:
        if not value:
            return None
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("vence debe tener el formato YYYY-MM-DD") from exc
        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(BaseModel):
    codigo: str
    nombre: str
    categoria: str
    presentacion: str
    cantidad: int
    ubicacion: str
    vence: str
    estado: str
    estado_clase: EstadoClase


class ShoppingItemCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    cantidad: int = Field(default=1, ge=0)


class ShoppingItemUpdate(BaseModel):
    cantidad_compra: Optional[int] = Field(default=None, ge=0)
    comprado: Optional[bool] = None


class ShoppingItemOut(BaseModel):
    codigo: str
    nombre: str
    presentacion: Optional[str] = None
    cantidad_inventario: Optional[int] = None
    compra_cantidad: int
    comprado: bool
    personalizado: bool


class LoginIn(BaseModel):
    username: str
    password: str


class RegistroIn(BaseModel):
    username: str
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    username: str
    id_casa: int