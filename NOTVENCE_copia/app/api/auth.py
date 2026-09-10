from fastapi import APIRouter, Depends, HTTPException, status

from app import products_repo
from app.deps import get_current_casa, get_current_user
from app.schemas import LoginIn, RegistroIn, TokenOut, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/auth/login", response_model=TokenOut)
def login(datos: LoginIn):
    conexion = products_repo.get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT nombre, contrasena FROM usuario WHERE nombre = %s",
        (datos.username,),
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not usuario or not verify_password(datos.password, usuario[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    token = create_access_token(usuario[0])
    return TokenOut(access_token=token)


@router.post("/auth/registro", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroIn):
    conexion = products_repo.get_connection()
    cursor = conexion.cursor()

    cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (datos.email,))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese correo ya está registrado.",
        )

    nombre_casa = f"Casa de {datos.username}"
    cursor.execute("INSERT INTO casa (nombre_hogar) VALUES (%s)", (nombre_casa,))
    id_casa = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO usuario (id_casa, nombre, correo, contrasena)
        VALUES (%s, %s, %s, %s)
        """,
        (id_casa, datos.username, datos.email, hash_password(datos.password)),
    )
    conexion.commit()
    cursor.close()
    conexion.close()

    token = create_access_token(datos.username)
    return TokenOut(access_token=token)


@router.get("/auth/me", response_model=UserOut, summary="Datos del usuario autenticado")
def me(user: str = Depends(get_current_user), id_casa: int = Depends(get_current_casa)):
    return UserOut(username=user, id_casa=id_casa)