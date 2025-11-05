# tienda/urls.py
from django.urls import path
from . import views

app_name = "tienda"

urlpatterns = [
    # Home / público
    path("", views.home, name="home"),
    path("carrito/", views.carrito, name="carrito"),
    path("checkout/", views.checkout, name="checkout"),
    path("catalogo/", views.catalogo, name="catalogo"),

    # Productos
    path("productos/", views.ProductoListView.as_view(), name="producto_list"),
    path("productos/nuevo/", views.ProductoCreateView.as_view(), name="producto_create"),
    path("productos/<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="producto_update"),
    path("productos/export/csv/", views.producto_export_csv, name="producto_export_csv"),
    path("productos/import/csv/", views.producto_import_csv, name="producto_import_csv"),

    # Clientes
    path("clientes/", views.ClienteListView.as_view(), name="cliente_list"),
    path("clientes/nuevo/", views.ClienteCreateView.as_view(), name="cliente_create"),
    path("clientes/<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="cliente_update"),

    # Ventas
    path("ventas/", views.VentaListView.as_view(), name="venta_list"),
    path("ventas/nueva/", views.venta_crear, name="venta_create"),
    path("ventas/<int:pk>/", views.VentaDetailView.as_view(), name="venta_detail"),
    path("ventas/<int:pk>/pdf/", views.venta_pdf, name="venta_pdf"),
]
