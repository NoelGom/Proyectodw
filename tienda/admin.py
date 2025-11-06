from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio_por_litro", "stock", "activo")
    search_fields = ("nombre", "tipo")
    list_filter = ("activo",)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "telefono", "nit")
    search_fields = ("nombre", "nit")

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "cliente", "total")
    date_hierarchy = "fecha"
    inlines = [DetalleVentaInline]
