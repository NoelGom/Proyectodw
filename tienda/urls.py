from django.urls import path
from . import views

urlpatterns = [
    # Productos
    path('productos/', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_edit, name='producto_new'),
    path('productos/<int:pk>/editar/', views.producto_edit, name='producto_edit'),

    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_edit, name='cliente_new'),
    path('clientes/<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),

    # Ventas
    path('ventas/', views.venta_list, name='venta_list'),
    path('ventas/nueva/', views.venta_create, name='venta_create'),

    # Catálogo
    path('catalogo/', views.catalogo, name='catalogo'),

    
    path('api/productos/<int:pk>/precio/', views.api_precio_producto, name='api_precio_producto'),
]
