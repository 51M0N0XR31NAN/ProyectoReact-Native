"""Dependencias de autenticación compartidas entre las páginas HTML y la API JSON."""
from fastapi import HTTPException, Request, status

from app.database import get_connection

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


def get_current_user(request: Request) -> str:
    """Dependencia para la API JSON: exige sesión activa o responde 401."""
    username = current_user(request)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión para usar la API.",
        )
    return username
