from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Cliente, Venta, DetalleVenta

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "tipo", "precio_litro", "stock_litros", "activo"]

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombres", "apellidos", "telefono", "nit", "direccion"]

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "litros", "precio_unitario"]

# Dejamos varias filas por defecto y SIN botón add_prefix en el template
DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    fields=["producto", "litros", "precio_unitario"],
    extra=3,              # 3 filas en blanco por defecto
    can_delete=True,
    min_num=1,
    validate_min=True,
)
