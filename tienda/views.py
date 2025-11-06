from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.urls import reverse
from decimal import Decimal
from .models import Producto, Cliente, Venta, DetalleVenta
from .forms import ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet


def producto_list(request):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.all().order_by('nombre')
    if q:
        productos = productos.filter(nombre__icontains=q)
    return render(request, 'tienda/producto_list.html', {'productos': productos})

def producto_edit(request, pk=None):
    instance = get_object_or_404(Producto, pk=pk) if pk else None
    form = ProductoForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('tienda:producto_list')
    return render(request, 'tienda/producto_form.html', {'form': form})


def cliente_list(request):
    q = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all().order_by('nombre')
    if q:
        clientes = clientes.filter(nombre__icontains=q)
    return render(request, 'tienda/cliente_list.html', {'clientes': clientes})

def cliente_edit(request, pk=None):
    instance = get_object_or_404(Cliente, pk=pk) if pk else None
    form = ClienteForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('tienda:cliente_list')
    return render(request, 'tienda/cliente_form.html', {'form': form})


def venta_list(request):
    ventas = Venta.objects.select_related('cliente').order_by('-id')
    return render(request, 'tienda/venta_list.html', {'ventas': ventas})

@transaction.atomic
def venta_create(request):
    form = VentaForm(request.POST or None)
    formset = DetalleVentaFormSet(request.POST or None, prefix='d')
   
    product_prices = {p.id: str(p.precio_por_litro) for p in Producto.objects.all()}
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        venta = form.save(commit=False)
        venta.total = Decimal('0')
        venta.save()

        total = Decimal('0')
        detalles = formset.save(commit=False)
        for d in detalles:
            d.venta = venta
           
            if not d.precio_unitario or d.precio_unitario == 0:
                d.precio_unitario = d.producto.precio_por_litro or Decimal('0')
            d.save()
            total += d.litros * d.precio_unitario
         
            if d.producto:
                d.producto.stock = (d.producto.stock or 0) - (d.litros or 0)
                d.producto.save(update_fields=['stock'])

       
        for obj in formset.deleted_objects:
            obj.delete()

        venta.total = total
        venta.save(update_fields=['total'])
        return redirect('tienda:venta_list')

    return render(
        request,
        'tienda/venta_form.html',
        {'form': form, 'formset': formset, 'product_prices': product_prices}
    )


def api_precio_producto(request, pk):
    p = get_object_or_404(Producto, pk=pk)
    return JsonResponse({'precio': str(p.precio_por_litro)})


def catalogo(request):
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    return render(request, 'tienda/catalogo.html', {'productos': productos})
