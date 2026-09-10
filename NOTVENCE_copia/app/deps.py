"""Dependencias de autenticación compartidas entre las páginas HTML y la API JSON."""
from fastapi import HTTPException, Request, status

from app.database import get_connection
from app.security import decode_access_token

def get_db():
    connection = get_connection()
    try:
        yield connection
    finally:
        if connection.is_connected():
            connection.close()

def current_user(request: Request) -> str | None:
    """Obtiene el nombre del usuario desde las cookies, validando que exista en MySQL."""
    username = request.cookies.get("notvence_user")
    if not username:
        return None

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT 1 FROM usuario WHERE nombre = %s", (username,))
    existe = cursor.fetchone()
    cursor.close()
    conexion.close()

    return username if existe else None


def _user_from_bearer_token(request: Request) -> str | None:
    """Obtiene el usuario a partir del header 'Authorization: Bearer <token>' (app móvil)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.removeprefix("Bearer ").strip()
    return decode_access_token(token) if token else None


def get_current_user(request: Request) -> str:
    """Dependencia para la API JSON: acepta token Bearer (app móvil) o cookie (web);
    exige sesión activa o responde 401."""
    username = _user_from_bearer_token(request) or current_user(request)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión para usar la API.",
        )
    return username


def resolve_casa_id(username: str) -> int | None:
    """Obtiene el id_casa asociado a un usuario."""
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_casa FROM usuario WHERE nombre = %s", (username,))
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    return fila[0] if fila else None


def get_current_casa(request: Request) -> int:
    """Dependencia para la API JSON: resuelve el id_casa del usuario autenticado."""
    username = get_current_user(request)
    id_casa = resolve_casa_id(username)
    if id_casa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la casa del usuario.",
        )
    return id_casa
