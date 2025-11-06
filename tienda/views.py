from decimal import Decimal
import csv
from io import TextIOWrapper

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt

from .models import Producto, Cliente, Venta, DetalleVenta
from .forms import (
    ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet
)

# ------------------- PRODUCTOS -------------------

class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/producto_list.html"
    context_object_name = "productos"
    paginate_by = 20

    def get_queryset(self):
        qs = Producto.objects.all().order_by("nombre")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(tipo__icontains=q))
        return qs

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

def producto_export_csv(request):
    """Exporta todos los productos a CSV (si no hay, igual genera encabezados)."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="productos.csv"'
    writer = csv.writer(response)
    writer.writerow(["nombre", "tipo", "precio_por_litro", "stock", "activo"])
    for p in Producto.objects.all().order_by("nombre"):
        writer.writerow([p.nombre, p.tipo, p.precio_por_litro, p.stock, getattr(p, "activo", True)])
    return response

@csrf_exempt  
def producto_import_csv(request):
    """
    Importa CSV con encabezados: nombre,tipo,precio_por_litro,stock[,activo]
    Crea o actualiza por 'nombre'.
    """
    if request.method != "POST":
        
        return HttpResponse(
            '<form method="post" enctype="multipart/form-data">'
            '<input type="file" name="file" accept=".csv">'
            '<button type="submit">Importar</button>'
            "</form>"
        )

    f = request.FILES.get("file")
    if not f:
        return HttpResponse("No se envió archivo", status=400)


    text_file = TextIOWrapper(f.file, encoding="utf-8", errors="ignore")
    reader = csv.DictReader(text_file)

    created, updated = 0, 0
    for row in reader:
        nombre = (row.get("nombre") or "").strip()
        if not nombre:
            continue
        tipo = (row.get("tipo") or "").strip()
        precio_raw = (row.get("precio_por_litro") or "0").strip()
        stock_raw = (row.get("stock") or "0").strip()
        activo_raw = (row.get("activo") or "True").strip()

        try:
            precio = Decimal(precio_raw)
        except Exception:
            precio = Decimal("0")

        try:
            stock = int(stock_raw)
        except Exception:
            stock = 0

        activo = str(activo_raw).lower() not in ("false", "0", "no")

        obj, was_created = Producto.objects.update_or_create(
            nombre=nombre,
            defaults={
                "tipo": tipo,
                "precio_por_litro": precio,
                "stock": stock,
                "activo": activo,
            },
        )
        created += 1 if was_created else 0
        updated += 0 if was_created else 1

    return redirect("tienda:producto_list")

# ------------------- CLIENTES -------------------

class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 20

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

# ------------------- VENTAS -------------------

class VentaListView(ListView):
    model = Venta
    template_name = "tienda/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 20

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

def venta_pdf(request, pk):
   
    return HttpResponse("PDF temporal", content_type="text/plain")



def api_producto_precio(request, pk):
    prod = get_object_or_404(Producto, pk=pk)
    return JsonResponse({"precio_por_litro": str(prod.precio_por_litro)})

def catalogo(request):
    return render(request, "tienda/catalogo.html")



from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from .models import Producto

@require_GET
def api_producto_precio(request, pk: int):
    try:
        p = Producto.objects.get(pk=pk)
    except Producto.DoesNotExist:
        raise Http404("Producto no existe")

    return JsonResponse({"id": p.pk, "precio_por_litro": float(p.precio_por_litro)})
