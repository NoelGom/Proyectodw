from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
import csv, io

from .models import Producto, Cliente, Venta
from .forms import ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet


def home(request):
    return render(request, "tienda/home.html")

def carrito(request):
    return render(request, "tienda/carrito.html")

def checkout(request):
    return render(request, "tienda/checkout.html")

def catalogo(request):
    productos = Producto.objects.filter(activo=True).order_by("nombre")
    return render(request, "tienda/catalogo.html", {"productos": productos})

# -------- Productos --------
class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/producto_list.html"
    context_object_name = "productos"
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        qs = Producto.objects.all().order_by("nombre")
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

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

def producto_export_csv(request):
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = "attachment; filename=productos.csv"
    writer = csv.writer(resp)
    writer.writerow(["nombre", "tipo", "precio_por_litro", "stock", "activo"])
    for p in Producto.objects.all():
        writer.writerow([p.nombre, p.tipo, p.precio_por_litro, p.stock, int(p.activo)])
    return resp

@csrf_protect
@login_required
def producto_import_csv(request):
    if request.method != "POST":
        messages.error(request, "Método no permitido.")
        return redirect("tienda:producto_list")

    file = request.FILES.get("file")
    if not file:
        messages.error(request, "Debes subir un archivo CSV.")
        return redirect("tienda:producto_list")

    decoded = file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))

    creados, actualizados = 0, 0
    for row in reader:
        nombre = (row.get("nombre") or row.get("Nombre") or "").strip()
        if not nombre:
            continue
        defaults = {
            "tipo": (row.get("tipo") or "").strip(),
            "precio_por_litro": row.get("precio_por_litro") or row.get("precio") or 0,
            "stock": row.get("stock") or 0,
            "activo": str(row.get("activo") or "1").lower() in ("1", "true", "sí", "si"),
        }
        obj, created = Producto.objects.update_or_create(nombre=nombre, defaults=defaults)
        if created:
            creados += 1
        else:
            actualizados += 1

    messages.success(request, f"Importados {creados} nuevos y actualizados {actualizados}.")
    return redirect("tienda:producto_list")

# -------- Clientes --------
class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        qs = Cliente.objects.all().order_by("nombre")
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

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

# -------- Ventas --------
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
            messages.success(request, "Venta registrada correctamente.")
            return redirect("tienda:venta_list")
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta, prefix="det")
    return render(request, "tienda/venta_form.html", {"form": form, "formset": formset})

class VentaListView(ListView):
    model = Venta
    template_name = "tienda/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 10

class VentaDetailView(DetailView):
    model = Venta
    template_name = "tienda/venta_detail.html"
    context_object_name = "venta"


def venta_pdf(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    contenido = (
        f"Comprobante de Venta #{venta.id}\n"
        f"Fecha: {venta.fecha}\n"
        f"Cliente: {venta.cliente}\n"
        f"Total: {venta.total}\n"
        "\n(Exportación a PDF aún no implementada en producción.)\n"
    )
    return HttpResponse(contenido, content_type="text/plain; charset=utf-8")
