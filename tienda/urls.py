from django.urls import path
from . import views

urlpatterns = [
    # Productos
    path("", views.ProductoListView.as_view(), name="producto_list"),
    path("productos/", views.ProductoListView.as_view(), name="producto_list"),
    path("productos/nuevo/", views.producto_crear, name="producto_crear"),
    path("productos/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("productos/export/csv/", views.producto_export_csv, name="producto_export_csv"),
    path("productos/import/csv/", views.producto_import_csv, name="producto_import_csv"),

    # Clientes
    path("clientes/", views.ClienteListView.as_view(), name="cliente_list"),
    path("clientes/nuevo/", views.cliente_crear, name="cliente_crear"),
    path("clientes/<int:pk>/editar/", views.cliente_editar, name="cliente_editar"),

    # Ventas
    path("ventas/", views.VentaListView.as_view(), name="venta_list"),
    path("ventas/nueva/", views.venta_crear, name="venta_crear"),
    path("ventas/<int:pk>/pdf/", views.venta_pdf, name="venta_pdf"),

    # Catálogo
    path("catalogo/", views.catalogo, name="catalogo"),

    
    path("api/producto/<int:pk>/precio/", views.api_producto_precio, name="api_producto_precio"),
]
