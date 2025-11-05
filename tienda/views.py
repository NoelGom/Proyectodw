# tienda/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django.core.serializers.json import DjangoJSONEncoder

import csv, io, json

from .models import Producto, Cliente, Venta
from .forms import ProductoForm, ClienteForm, VentaForm, DetalleVentaFormSet



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
    paginate_by = 10

    def get_queryset(self):
        qs = Producto.objects.all().order_by("nombre")
        q = self.request.GET.get("q", "").strip()
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
    w = csv.writer(resp)
    w.writerow(["Nombre","Tipo","PrecioLitro","Stock","Activo"])
    for p in Producto.objects.all().order_by("nombre"):
        w.writerow([p.nombre, p.tipo, p.precio_litro, p.stock_litros, "1" if p.activo else "0"])
    return resp

def producto_import_csv(request):
    if request.method == "POST" and request.FILES.get("archivo"):
        f = io.TextIOWrapper(request.FILES["archivo"].file, encoding="utf-8")
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            Producto.objects.update_or_create(
                nombre=row["Nombre"].strip(),
                defaults={
                    "tipo": row.get("Tipo","jabon"),
                    "precio_litro": row.get("PrecioLitro", 0) or 0,
                    "stock_litros": row.get("Stock", 0) or 0,
                    "activo": row.get("Activo","1") in ("1","true","True"),
                }
            )
            count += 1
        messages.success(request, f"Importados {count} productos.")
        return redirect("tienda:producto_list")
    return render(request, "tienda/producto_import.html")


# ---------- Clientes ----------
class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        qs = Cliente.objects.all().order_by("apellidos","nombres")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombres__icontains=q) | qs.filter(apellidos__icontains=q)
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


# ---------- Ventas ----------
def venta_crear(request):
    precios_json = json.dumps(list(Producto.objects.values("id","precio_litro")),
                              cls=DjangoJSONEncoder)
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
                    return render(request, "tienda/venta_form.html",
                                  {"form": form, "formset": formset, "precios_json": precios_json})
            messages.success(request, "Venta registrada correctamente.")
            return redirect("tienda:venta_detail", pk=venta.pk)
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta, prefix="det")

    return render(request, "tienda/venta_form.html",
                  {"form": form, "formset": formset, "precios_json": precios_json})

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
   
    try:
        from xhtml2pdf import pisa
        venta = (Venta.objects.select_related("cliente")
                 .prefetch_related("detalles__producto").get(pk=pk))
        html = render(request, "tienda/venta_pdf.html", {"venta": venta}).content.decode("utf-8")
        result = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html), dest=result)
        pdf = result.getvalue()
    except Exception:
        pdf = b"%PDF-1.3\n%Minimal\n"
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp['Content-Disposition'] = f'inline; filename=venta_{pk}.pdf'
    return resp


# ---------- Reporte ----------
def reporte_ventas(request):
    f1 = parse_date(request.GET.get("desde","") or "")
    f2 = parse_date(request.GET.get("hasta","") or "")
    qs = Venta.objects.select_related("cliente").all()
    if f1: qs = qs.filter(fecha__date__gte=f1)
    if f2: qs = qs.filter(fecha__date__lte=f2)
    if request.GET.get("csv") == "1":
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = "attachment; filename=reporte_ventas.csv"
        w = csv.writer(resp)
        w.writerow(["ID","Fecha","Cliente","Total"])
        for v in qs:
            w.writerow([v.id, v.fecha.strftime("%Y-%m-%d %H:%M"), str(v.cliente), f"{v.total}"])
        return resp
    return render(request, "tienda/reporte_ventas.html", {"ventas": qs, "desde": f1, "hasta": f2})
