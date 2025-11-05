# tienda/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
from django.db.models import Q

from .models import Producto, Cliente, Venta, DetalleVenta
from .forms import (
    ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet
)

class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/producto_list.html"
    context_object_name = "productos"
    paginate_by = 20

    def get_queryset(self):
        qs = Producto.objects.all().order_by("nombre")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(tipo__icontains=q)
            )
        return qs

# ------- Resto de vistas (resumen necesario para que no falle URLs) ------

class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 20

def producto_crear(request):
    form = ProductoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("tienda:producto_list")
    return render(request, "tienda/producto_form.html", {"form": form})

def producto_editar(request, pk):
    obj = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("tienda:producto_list")
    return render(request, "tienda/producto_form.html", {"form": form})

def cliente_crear(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("tienda:cliente_list")
    return render(request, "tienda/cliente_form.html", {"form": form})

def cliente_editar(request, pk):
    obj = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("tienda:cliente_list")
    return render(request, "tienda/cliente_form.html", {"form": form})

def venta_crear(request):
    venta_form = VentaForm(request.POST or None)
    formset = DetalleVentaFormSet(request.POST or None, prefix="det")
    if request.method == "POST" and venta_form.is_valid() and formset.is_valid():
        venta = venta_form.save()
        detalles = formset.save(commit=False)
        for d in detalles:
            d.venta = venta
            d.save()
        return redirect("tienda:venta_list")
    return render(request, "tienda/venta_form.html", {
        "form": venta_form,
        "formset": formset,
    })

class VentaListView(ListView):
    model = Venta
    template_name = "tienda/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 20

def venta_pdf(request, pk):
    # Placeholder para no romper rutas
    return HttpResponse("PDF temporal", content_type="text/plain")

def catalogo(request):
    return render(request, "tienda/catalogo.html")

def api_producto_precio(request, pk):
    prod = get_object_or_404(Producto, pk=pk)
    return JsonResponse({"precio_por_litro": str(prod.precio_por_litro)})
