from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta, LogAccion

class DetalleInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "cliente", "total")
    inlines = [DetalleInline]

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre","tipo","precio_litro","stock_litros","activo")
    search_fields = ("nombre",)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombres","apellidos","telefono","nit")
    search_fields = ("nombres","apellidos","nit")

@admin.register(LogAccion)
class LogAccionAdmin(admin.ModelAdmin):
    list_display = ("fecha_hora","evento","modelo","pk_obj","usuario")
    readonly_fields = ("fecha_hora","evento","modelo","pk_obj","payload","usuario")
