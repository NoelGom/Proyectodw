from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
import json

from .models import Producto, Cliente, Venta
from .forms import ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet

# ---------- Home / simples ----------
def home(request):
    return render(request, "tienda/home.html")

def carrito(request):
    return render(request, "tienda/carrito.html")

def checkout(request):
    return render(request, "tienda/checkout.html")

def catalogo(request):
    productos = Producto.objects.filter(activo=True).order_by("nombre")[:50]
    return render(request, "tienda/catalogo.html", {"productos": productos})

# ---------- Productos ----------
class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "tienda/producto_list.html"
    context_object_name = "productos"
    paginate_by = 10
    def get_queryset(self):
        qs = Producto.objects.all().order_by("nombre")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/producto_form.html"
    success_url = reverse_lazy("tienda:producto_list")

class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/producto_form.html"
    success_url = reverse_lazy("tienda:producto_list")

# ---------- Clientes ----------
class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 10
    def get_queryset(self):
        qs = Cliente.objects.all().order_by("apellidos", "nombres")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombres__icontains=q) | qs.filter(apellidos__icontains=q)
        return qs

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("tienda:cliente_list")

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("tienda:cliente_list")

# ---------- Ventas ----------
@login_required
def venta_crear(request):
    # Prepara un JSON { id: precio_litro } para autocompletar precios en el template
    precios_json = json.dumps(
        list(Producto.objects.values("id", "precio_litro")),
        cls=DjangoJSONEncoder
    )

    venta = Venta()
    if request.method == "POST":
        form = VentaForm(request.POST, instance=venta)
        formset = DetalleVentaFormSet(request.POST, instance=venta, prefix="det")
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = form.save()
                formset.instance = venta
                formset.save()
                try:
                    venta.confirmar()
                except ValueError as e:
                    transaction.set_rollback(True)
                    messages.error(request, str(e))
                    return render(
                        request,
                        "tienda/venta_form.html",
                        {"form": form, "formset": formset, "precios_json": precios_json},
                    )
            messages.success(request, "Venta registrada correctamente.")
            return redirect("tienda:venta_detail", pk=venta.pk)
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta, prefix="det")

    return render(
        request,
        "tienda/venta_form.html",
        {"form": form, "formset": formset, "precios_json": precios_json},
    )

class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = "tienda/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 10

class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = "tienda/venta_detail.html"
    context_object_name = "venta"
