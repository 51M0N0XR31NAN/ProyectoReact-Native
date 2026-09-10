"""Almacen de datos en memoria compartido entre las paginas HTML y la API JSON."""
from datetime import date, datetime

# =================
# DATOS EN MEMORIA 
# =================

# Presentaciones por categoría
PRESENTATIONS = {
    "Alimentos": ["Unidad", "Kg", "Gramos (g)", "Libra (lb)", "Litro (L)", "Mililitro (ml)",
                  "Paquete", "Bolsa", "Caja", "Lata", "Frasco", "Botella", "Tarro", "Tubo",
                  "Bandeja", "Racimo", "Docena", "Media docena", "Porción", "Sobre", "Pote",
                  "Rollo", "Rebanada", "Unidad individual"],
    "Bebidas": ["Litro (L)", "Mililitro (ml)", "Galón", "Botella", "Lata", "Caja", "Paquete",
                "Bolsa", "Frasco", "Tarro", "Vaso", "Sobre", "Unidad", "Garrafón", "Botellón"],
    "Aseo": ["Unidad", "Litro (L)", "Mililitro (ml)", "Kg", "Gramos (g)", "Bolsa", "Paquete",
             "Caja", "Botella", "Frasco", "Tarro", "Galón", "Rollo", "Unidad individual",
             "Sobre", "Pote", "Aerosol", "Pastilla", "Barra", "Kit", "Recarga", "Repósito/recarga"],
    "Medicamentos": ["Unidad", "Tableta", "Cápsula", "Comprimido", "Pastilla", "Sobre",
                     "Ampolla", "Vial", "Frasco", "Botella", "Tubo", "Crema", "Gel", "Pomada",
                     "Jarabe", "Gotas", "Spray", "Inhalador", "Parche", "Supositorio", "Jeringa",
                     "Caja", "Blíster", "Paquete"],
    "Otros": ["Unidad", "Kg", "Gramos (g)", "Litro (L)", "Mililitro (ml)", "Paquete", "Bolsa",
             "Caja", "Botella", "Frasco", "Tarro", "Galón", "Rollo", "Sobre", "Tubo", "Kit",
             "Juego", "Par", "Docena", "Metro", "Centímetro", "Pieza", "Set", "Bandeja",
             "Bulto", "Recarga", "Envase", "Contenedor"],
}


# ======================
# FUNCIONES AUXILIARES
# ======================

def product_status(quantity, expiration):
    """Determina TODAS las alertas activas de un producto según cantidad y
    fecha de vencimiento (un producto puede tener varias a la vez, por
    ejemplo estar vencido y además con stock bajo). Devuelve una lista de
    tuplas (etiqueta, clase_css); si no hay ninguna alerta, devuelve
    [("Activo", "success")]."""
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 0

    alerts: list[tuple[str, str]] = []

    # Alerta de stock bajo
    if quantity <= 3:
        alerts.append(("Stock bajo", "danger"))

    # Alerta de vencimiento (vencido o por vencer son mutuamente excluyentes entre sí,
    # pero sí pueden coexistir con la de stock bajo)
    if expiration:
        try:
            expiration_date = datetime.strptime(expiration, "%Y-%m-%d").date()
            days_left = (expiration_date - date.today()).days
            if days_left < 0:
                alerts.append(("Vencido", "danger"))
            elif days_left <= 7:
                alerts.append(("Por vencer", "warning"))
        except ValueError:
            pass

    # Si no hay ninguna alerta, el producto está activo
    if not alerts:
        alerts.append(("Activo", "success"))

    return alerts
