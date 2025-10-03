from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ("subtotal",)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio_litro", "stock_litros", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre",)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombres", "apellidos", "telefono", "nit")
    search_fields = ("nombres", "apellidos", "nit")

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "fecha", "total")
    date_hierarchy = "fecha"
    inlines = [DetalleVentaInline]
