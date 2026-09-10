"""Migra las contraseñas de texto plano a hash bcrypt en la tabla `usuario`.

Es seguro ejecutarlo varias veces: las filas cuya contraseña ya está
hasheada (empieza por $2a$/$2b$/$2y$) se dejan sin tocar.

Uso:
    python -m scripts.migrar_passwords
"""
from app.database import get_connection
from app.security import hash_password


def ya_esta_hasheada(valor: str) -> bool:
    return valor.startswith(("$2a$", "$2b$", "$2y$"))


def main() -> None:
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario, nombre, contrasena FROM usuario")
    usuarios = cursor.fetchall()

    migrados = 0
    for id_usuario, nombre, contrasena in usuarios:
        if ya_esta_hasheada(contrasena):
            continue
        nuevo_hash = hash_password(contrasena)
        cursor.execute(
            "UPDATE usuario SET contrasena = %s WHERE id_usuario = %s",
            (nuevo_hash, id_usuario),
        )
        migrados += 1
        print(f"Migrado: {nombre} (id_usuario={id_usuario})")

    conexion.commit()
    cursor.close()
    conexion.close()
    print(f"\nListo. {migrados} de {len(usuarios)} usuarios migrados a bcrypt.")


if __name__ == "__main__":
    main()
