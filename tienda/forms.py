from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Cliente, Venta, DetalleVenta

def _has(model, field_name: str) -> bool:
    return field_name in {f.name for f in model._meta.get_fields()}

_prod_candidates = ["nombre", "tipo", "precio_litro", "stock_litros", "activo"]
_prod_fields = [f for f in _prod_candidates if _has(Producto, f)]

if not _prod_fields:
    _prod_fields = "__all__"

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = _prod_fields


if _has(Cliente, "nombre"):
    _cli_fields = ["nombre"]
else:
    _cli_fields = [f for f in ("nombres", "apellidos") if _has(Cliente, f)]

for opt in ("telefono", "nit"):
    if _has(Cliente, opt):
        _cli_fields.append(opt)

if not _cli_fields:
    _cli_fields = "__all__"

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = _cli_fields

# ---------- Venta / Detalle ----------
_venta_fields = ["cliente"] if _has(Venta, "cliente") else "__all__"

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = _venta_fields

_det_fields = [f for f in ("producto", "litros", "precio_unitario") if _has(DetalleVenta, f)]
if not _det_fields:
    _det_fields = "__all__"

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = _det_fields

DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    fields=_det_fields if _det_fields != "__all__" else None,  # None = usa Meta.fields
    extra=4,
    can_delete=True,
)
