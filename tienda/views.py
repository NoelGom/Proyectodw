from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm, DetalleVentaFormSet, ProductoForm, VentaForm
from .models import Cliente, DetalleVenta, Producto, Venta


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
    clientes = Cliente.objects.all().order_by('apellidos', 'nombres')
    if q:
        clientes = clientes.filter(Q(nombres__icontains=q) | Q(apellidos__icontains=q))
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
   
    product_prices = {p.id: str(p.precio_litro) for p in Producto.objects.all()}
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        venta = form.save()
        detalles = formset.save(commit=False)
        for d in detalles:
            d.venta = venta

            if not d.precio_unitario:
                d.precio_unitario = d.producto.precio_litro or Decimal('0')
            d.save()


        for obj in formset.deleted_objects:
            obj.delete()

        try:
            venta.confirmar()
        except ValueError as exc:
            transaction.set_rollback(True)
            form.add_error(None, str(exc))
        else:
            return redirect('tienda:venta_list')

    return render(
        request,
        'tienda/venta_form.html',
        {'form': form, 'formset': formset, 'product_prices': product_prices}
    )


def api_precio_producto(request, pk):
    p = get_object_or_404(Producto, pk=pk)
    return JsonResponse({'precio': str(p.precio_litro)})


def catalogo(request):
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    return render(request, 'tienda/catalogo.html', {'productos': productos})
