from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio_litro", "stock_litros", "activo")
    search_fields = ("nombre", "tipo")
    list_filter = ("activo",)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "telefono", "nit")
    search_fields = ("nombres", "apellidos", "nit")

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "cliente", "total")
    date_hierarchy = "fecha"
    inlines = [DetalleVentaInline]
