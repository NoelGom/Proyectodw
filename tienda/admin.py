from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio_por_litro", "stock", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre",)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "telefono", "nit")
    search_fields = ("nombre", "nit")

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "fecha", "total")
    list_select_related = ("cliente",)
    inlines = [DetalleVentaInline]

