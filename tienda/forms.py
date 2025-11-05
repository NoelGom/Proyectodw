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
        widgets = {
            "litros": forms.NumberInput(attrs={"step":"0.01", "min":"0.01"}),
            "precio_unitario": forms.NumberInput(attrs={"step":"0.01", "readonly":"readonly"}),
        }

    def clean(self):
        cleaned = super().clean()
        prod = cleaned.get("producto")
        litros = cleaned.get("litros")
        if prod and litros and litros > prod.stock_litros:
            raise forms.ValidationError(f"Stock insuficiente de {prod.nombre}. Disponible: {prod.stock_litros} L.")
        return cleaned

DetalleVentaFormSet = inlineformset_factory(
    Venta, DetalleVenta, form=DetalleVentaForm,
    fields=["producto", "litros", "precio_unitario"],
    extra=3, can_delete=True, min_num=1, validate_min=True
)
