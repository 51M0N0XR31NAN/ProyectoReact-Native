from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import products_repo
from app.database import get_connection
from app.api import router as api_router
from app.deps import current_user
from app.security import hash_password, verify_password

# =======================================
# INICIALIZACIÓN DE LA APLICACIÓN FASTAPI
# =======================================

app = FastAPI(title="NOTVENCE")

# Configurar el directorio de templates (HTML)
templates = Jinja2Templates(directory="app/templates")

# Montar la carpeta /static para servir archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Montar la API JSON bajo el prefijo /api
app.include_router(api_router)

# Permitir que la app React Native (Expo, en otro origen/host) consuma la API.
# En desarrollo se permite cualquier origen; para producción conviene restringirlo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_cache_paginas(request: Request, call_next):
   
    response = await call_next(request)
    if not request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# =====================
# FUNCIONES AUXILIARES
# ======================

async def read_form(request: Request):
    body = (await request.body()).decode("utf-8")
    return {key: values[0] for key, values in parse_qs(body).items()}


# Verifica si hay un usuario logueado; si no, redirige a login
def require_user(request: Request):
    username = current_user(request)
    if not username:
        # Retornar None y una redirección si no está autenticado
        return None, RedirectResponse(url="/?error=Debes iniciar sesión con una cuenta registrada.", status_code=303)
    return username, None

def current_user_casa(request: Request):
    """Obtiene el id de la casa asociada al usuario actual."""

    username = current_user(request)

    if not username:
        return None

    conexion = products_repo.get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_casa
        FROM usuario
        WHERE nombre = %s
        """,
        (username,)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not usuario:
        return None

    return usuario[0]


def current_products(id_casa: int):
    """Productos del inventario de una casa, respaldados por MySQL (ver app/products_repo.py)."""
    return products_repo.list_products(id_casa)



# ======================
# RUTAS DE AUTENTICACIÓN
# =======================

@app.get("/")
def login(request: Request, error: str | None = None, success: str | None = None):
    """Página de login/registro. Muestra registro si no hay usuarios, login si los hay."""
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT 1 FROM usuario LIMIT 1")
    hay_usuarios = cursor.fetchone() is not None
    cursor.close()
    conexion.close()

    mode = "login" if hay_usuarios else "register"
    return templates.TemplateResponse(
        request,
        "login_page.html",
        {"request": request, "error": error, "success": success, "mode": mode}
    )


@app.post("/registro")
async def register_post(request: Request):
    """Registra un usuario y crea automáticamente su casa."""

    form = await read_form(request)

    username = form.get("username", "").strip()
    email = form.get("email", "").strip()
    password = form.get("password", "").strip()

    # Validar campos
    if not username or not email or not password:
        return RedirectResponse(
            url="/?error=Completa usuario, correo y contraseña.",
            status_code=303
        )

    conexion = products_repo.get_connection()
    cursor = conexion.cursor()

    # Verificar si el correo ya existe
    cursor.execute(
        "SELECT id_usuario FROM usuario WHERE correo = %s",
        (email,)
    )

    if cursor.fetchone():
        cursor.close()
        conexion.close()

        return RedirectResponse(
            url="/?error=Ese correo ya está registrado.",
            status_code=303
        )

    # Crear automáticamente la casa
    nombre_casa = f"Casa de {username}"

    cursor.execute(
        """
        INSERT INTO casa (nombre_hogar)
        VALUES (%s)
        """,
        (nombre_casa,)
    )

    id_casa = cursor.lastrowid

    # Crear el usuario relacionado con la casa
    cursor.execute(
        """
        INSERT INTO usuario (id_casa, nombre, correo, contrasena)
        VALUES (%s, %s, %s, %s)
        """,
        (id_casa, username, email, hash_password(password))
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return RedirectResponse(
        url="/?success=Cuenta creada. Ahora inicia sesión.",
        status_code=303
    )


@app.post("/login")
async def login_post(request: Request):
    """Valida las credenciales usando MySQL."""

    form = await read_form(request)

    username = form.get("username", "").strip()
    password = form.get("password", "").strip()

    if not username or not password:
        return RedirectResponse(
            url="/?error=Completa usuario y contraseña.",
            status_code=303
        )

    conexion = products_repo.get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_usuario, nombre, contrasena
        FROM usuario
        WHERE nombre = %s
        """,
        (username,)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    # Verificar usuario y contraseña
    if not usuario or not verify_password(password, usuario[2]):
        return RedirectResponse(
            url="/?error=Usuario o contraseña incorrectos.",
            status_code=303
        )

    # Crear sesión
    response = RedirectResponse(
        url="/inventario",
        status_code=303
    )

    response.set_cookie(
        "notvence_user",
        username,
        httponly=True,
        samesite="lax"
    )

    return response

@app.get("/logout")
def logout():
    """Cierra la sesión eliminando la cookie."""
    response = RedirectResponse(url="/?success=Sesión cerrada.", status_code=303)
    response.delete_cookie("notvence_user")
    return response


# ============================================================================
# RUTAS PRINCIPALES DE LA APLICACIÓN
# ============================================================================


@app.get("/inventario")
def inventario(request: Request):
    """Muestra la tabla completa de productos del inventario."""
    username, redirect = require_user(request)
    if redirect:
        return redirect

    id_casa = current_user_casa(request)
    if id_casa is None:
        return RedirectResponse(url="/?error=No se encontró la casa del usuario.", status_code=303)

    products = current_products(id_casa)
    return templates.TemplateResponse(
        request,
        "inventario_page.html",
        {"request": request, "current_page": "inventario", "user": username, "products": products}
    )

@app.get("/producto/nuevo")
def nuevo_producto(request: Request):
    """Muestra el formulario para crear un nuevo producto."""
    username, redirect = require_user(request)

    if redirect:
        return redirect

    return templates.TemplateResponse(
        request,
        "producto_nuevo_page.html",
        {
            "request": request,
            "current_page": "producto",
            "user": username
        }
    )

@app.post("/producto/nuevo")
async def crear_producto(request: Request):
    """Procesa el formulario de nuevo producto y lo guarda en MySQL."""

    username, redirect = require_user(request)

    if redirect:
        return redirect

    id_casa = current_user_casa(request)

    if id_casa is None:
        return RedirectResponse(
            url="/inventario?error=No se encontró la casa del usuario.",
            status_code=303
        )

    form = await read_form(request)

    quantity = form.get("cantidad", "0").strip() or "0"
    expiration = form.get("vence", "").strip()
    categoria = form.get("categoria", "Otros").strip()

    producto = products_repo.create_product({
        "nombre": form.get("nombre", "").strip() or "Producto sin nombre",
        "categoria": categoria,
        "descripcion": form.get("descripcion", "").strip(),
        "presentacion": form.get("presentacion", "").strip() or "Unidad",
        "cantidad": int(float(quantity)),
        "ubicacion": form.get("ubicacion", "").strip(),
        "vence": expiration or None,
    }, id_casa)

    if producto is None:
        return RedirectResponse(
            url="/producto/nuevo?error=Categoría no encontrada.",
            status_code=303
        )

    return RedirectResponse(
        url="/inventario?success=Producto registrado correctamente.",
        status_code=303
    )

@app.get("/producto/{codigo}")
def detalle_producto(request: Request, codigo: str):
    """READ: ruta dinamica que muestra un producto segun su codigo."""
    username, redirect = require_user(request)
    if redirect:
        return redirect

    id_casa = current_user_casa(request)
    product = products_repo.get_product(codigo, id_casa) if id_casa is not None else None
    if not product:
        return RedirectResponse(url="/inventario?error=Producto no encontrado.", status_code=303)

    return templates.TemplateResponse(
        request,
        "producto_detalle_page.html",
        {"request": request, "current_page": "inventario", "user": username, "product": product}
    )


@app.get("/producto/{codigo}/editar")
def editar_producto(request: Request, codigo: str):
    """UPDATE: muestra el formulario para editar un producto existente."""
    username, redirect = require_user(request)
    if redirect:
        return redirect

    id_casa = current_user_casa(request)
    product = products_repo.get_product(codigo, id_casa) if id_casa is not None else None
    if not product:
        return RedirectResponse(url="/inventario?error=Producto no encontrado.", status_code=303)

    return templates.TemplateResponse(
        request,
        "producto_editar_page.html",
        {"request": request, "current_page": "inventario", "user": username, "product": product}
    )


@app.post("/producto/{codigo}/editar")
async def actualizar_producto(request: Request, codigo: str):
    """UPDATE: guarda cambios en el producto en MySQL."""
    username, redirect = require_user(request)
    if redirect:
        return redirect

    id_casa = current_user_casa(request)
    if id_casa is None:
        return RedirectResponse(url="/inventario?error=No se encontró la casa del usuario.", status_code=303)

    form = await read_form(request)
    quantity = form.get("cantidad", "0").strip() or "0"
    expiration = form.get("vence", "").strip()

    producto = products_repo.update_product(codigo, {
        "nombre": form.get("nombre", "").strip() or "Producto sin nombre",
        "categoria": form.get("categoria", "Otros").strip(),
        "presentacion": form.get("presentacion", "").strip() or "Unidad",
        "cantidad": int(quantity),
        "ubicacion": form.get("ubicacion", "").strip(),
        "vence": expiration or None,
    }, id_casa)

    if producto is None:
        return RedirectResponse(url="/inventario?error=Producto no encontrado.", status_code=303)

    return RedirectResponse(url=f"/producto/{codigo}?success=Producto actualizado.", status_code=303)


@app.post("/producto/{codigo}/eliminar")
async def eliminar_producto(request: Request, codigo: str):
    """DELETE: elimina un producto del inventario en MySQL."""
    username, redirect = require_user(request)
    if redirect:
        return redirect

    id_casa = current_user_casa(request)
    eliminado = products_repo.delete_product(codigo, id_casa) if id_casa is not None else False
    if not eliminado:
        return RedirectResponse(url="/inventario?error=Producto no encontrado.", status_code=303)


    return RedirectResponse(url="/inventario?success=Producto eliminado.", status_code=303)


@app.get("/alertas")
def alertas(request: Request):

    """Muestra productos con estado no activo (alertas)."""

    username, redirect = require_user(request)

    if redirect:
        return redirect

    id_casa = current_user_casa(request)

    if id_casa is None:
        return RedirectResponse(
            url="/?error=No se encontró la casa del usuario.",
            status_code=303
        )

    products = products_repo.list_products(id_casa)

    alert_products = [
        product for product in products
        if product["estado"] != "Activo"
    ]

    return templates.TemplateResponse(
        request,
        "alertas_page.html",
        {
            "request": request,
            "current_page": "alertas",
            "user": username,
            "alert_products": alert_products
        }
    )


@app.get("/prueba-db")
def prueba_db():
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()

        cursor.close()
        conexion.close()

        return {
            "mensaje": "Conexión exitosa con la base de datos",
            "resultado": resultado[0]
        }

    except Exception as e:
        return {
            "mensaje": "Error al conectar con la base de datos",
            "error": str(e)
        }
