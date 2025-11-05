from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Cliente, Venta, DetalleVenta


def _has(model, field_name: str) -> bool:
    return field_name in {f.name for f in model._meta.get_fields()}


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
    fields = ["nombre", "tipo", "precio_litro", "stock_litros", "activo"]


if _has(Cliente, "nombre"):
    _cliente_fields = ["nombre"]

elif _has(Cliente, "nombres") and _has(Cliente, "apellidos"):
    _cliente_fields = ["nombres", "apellidos"]
else:

    _char_fields = [f.name for f in Cliente._meta.get_fields() if getattr(getattr(f, "get_internal_type", lambda: "")(), "") == "CharField"]
    _cliente_fields = _char_fields[:1] or []


for optional in ("telefono", "nit"):
    if _has(Cliente, optional):
        _cliente_fields.append(optional)

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = _cliente_fields


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        
        fields = ["cliente"] if _has(Venta, "cliente") else []

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = [f for f in ("producto", "litros", "precio_unitario") if _has(DetalleVenta, f)]

DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    fields=[f for f in ("producto", "litros", "precio_unitario") if _has(DetalleVenta, f)],
    extra=4,
    can_delete=True,
)
