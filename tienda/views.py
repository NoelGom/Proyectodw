from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse

from .models import Producto, Cliente, Venta
from .forms import ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet

# ---------- Home / páginas simples ----------
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
class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/producto_list.html"
    context_object_name = "productos"

class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/producto_form.html"
    success_url = reverse_lazy("tienda:producto_list")

class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/producto_form.html"
    success_url = reverse_lazy("tienda:producto_list")

# ---------- Clientes ----------
class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"

class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("tienda:cliente_list")

class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("tienda:cliente_list")

# ---------- Ventas ----------
def venta_crear(request):
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
                    # volver a renderizar con datos cargados
                    return render(request, "tienda/venta_form.html", {"form": form, "formset": formset})
            messages.success(request, "Venta registrada correctamente.")
            return redirect("tienda:venta_detail", pk=venta.pk)
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta, prefix="det")
    return render(request, "tienda/venta_form.html", {"form": form, "formset": formset})

class VentaListView(ListView):
    model = Venta
    template_name = "tienda/venta_list.html"
    context_object_name = "ventas"

class VentaDetailView(DetailView):
    model = Venta
    template_name = "tienda/venta_detail.html"
    context_object_name = "venta"
