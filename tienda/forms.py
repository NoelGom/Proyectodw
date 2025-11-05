from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Cliente, Venta, DetalleVenta

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "tipo", "precio_por_litro", "stock", "activo"]

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "telefono", "nit"]

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "litros", "precio_unitario"]

DetalleVentaFormSet = inlineformset_factory(
    Venta, DetalleVenta,
    form=DetalleVentaForm,
    fields=["producto", "litros", "precio_unitario"],
    extra=4, can_delete=True,
)
