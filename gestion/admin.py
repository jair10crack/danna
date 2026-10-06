from django.contrib import admin
from gestion.models import (
    Usuario,
    Categoria,
    Proveedor,
    Producto,
    Cliente,
    Venta,
    DetalleVenta,
    MovimientoCuenta,
)

admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(MovimientoCuenta)
