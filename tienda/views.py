from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.db import transaction

from .models import Producto, Cliente, Venta, DetalleVenta
from .forms import (
    ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet
)

class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/producto_list.html"
    context_object_name = "productos"

class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"

class VentaListView(ListView):
    model = Venta
    template_name = "tienda/venta_list.html"
    context_object_name = "ventas"


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


@transaction.atomic
def venta_crear(request):
    venta_form = VentaForm(request.POST or None)
    formset = DetalleVentaFormSet(request.POST or None, prefix="det")

    if request.method == "POST":
        if venta_form.is_valid() and formset.is_valid():
            venta = venta_form.save()
            dets = formset.save(commit=False)
            for d in dets:
                d.venta = venta
             
                if not d.precio_unitario:
                    p = d.producto
                    precio = (
                        getattr(p, "precio_litro", None)
                        or getattr(p, "precio_por_litro", None)
                        or getattr(p, "precio", None)
                        or getattr(p, "precio_unitario", None)
                        or Decimal("0")
                    )
                    d.precio_unitario = precio
                d.save()
            for d in formset.deleted_objects:
                d.delete()
            return redirect("tienda:venta_list")

    return render(
        request,
        "tienda/venta_form.html",
        {"venta_form": venta_form, "formset": formset},
    )

def venta_pdf(request, pk):
   
    venta = get_object_or_404(Venta, pk=pk)
    return HttpResponse(f"PDF de venta #{venta.id}", content_type="text/plain")


def catalogo(request):
    productos = Producto.objects.all()
    return render(request, "tienda/catalogo.html", {"productos": productos})


def producto_export_csv(request):

    return HttpResponse("OK", content_type="text/plain")

def producto_import_csv(request):
  
    return HttpResponse("OK", content_type="text/plain")


def api_producto_precio(request, pk):
    """
    Devuelve {precio: <decimal>} para el producto PK.
    Toma cualquiera de los posibles nombres: precio_litro, precio_por_litro,
    precio, precio_unitario (soporta tus variantes).
    """
    prod = get_object_or_404(Producto, pk=pk)

    precio = (
        getattr(prod, "precio_litro", None)
        or getattr(prod, "precio_por_litro", None)
        or getattr(prod, "precio", None)
        or getattr(prod, "precio_unitario", None)
        or Decimal("0")
    )

  
    return JsonResponse({"precio": float(precio)})
