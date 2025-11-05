from decimal import Decimal, ROUND_HALF_UP
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import json

Q2 = Decimal("0.01")
User = get_user_model()

class Cliente(models.Model):
    nombres   = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono  = models.CharField(max_length=30, blank=True)
    nit       = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip()

class Producto(models.Model):
    TIPO_CHOICES = [
        ("jabon", "Jabón"),
        ("desinfectante", "Desinfectante"),
        ("suavizante", "Suavizante"),
    ]
    nombre        = models.CharField(max_length=120, unique=True)
    tipo          = models.CharField(max_length=20, choices=TIPO_CHOICES)
    precio_litro  = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    stock_litros  = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    activo        = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        indexes = [models.Index(fields=["activo", "tipo"])]

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    def clean(self):
        if self.precio_litro and self.precio_litro <= 0:
            raise ValidationError("El precio por litro debe ser mayor a 0.")
        if self.stock_litros is not None and self.stock_litros < 0:
            raise ValidationError("El stock no puede ser negativo.")

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ventas")
    fecha   = models.DateTimeField(default=timezone.now)
    total   = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta #{self.pk or '—'} - {self.fecha:%Y-%m-%d %H:%M}"

    def recalcular_total(self):
        agg = sum((d.subtotal for d in self.detalles.all()), Decimal("0.00"))
        self.total = Decimal(agg).quantize(Q2, rounding=ROUND_HALF_UP)
        return self.total

    @transaction.atomic
    def confirmar(self):
       
        detalles = self.detalles.select_related("producto").select_for_update(of=("self", "producto"))
        for det in detalles:
            if det.litros <= 0:
                raise ValueError("Los litros deben ser mayores a 0.")
            if det.litros > det.producto.stock_litros:
                raise ValueError(f"Stock insuficiente para {det.producto.nombre}. Disponible: {det.producto.stock_litros} L.")
        for det in detalles:
            prod = det.producto
            prod.stock_litros = (prod.stock_litros - det.litros).quantize(Q2, rounding=ROUND_HALF_UP)
            prod.save(update_fields=["stock_litros"])
        self.recalcular_total()
        self.save(update_fields=["total"])

class DetalleVenta(models.Model):
    venta           = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT)
    litros          = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self):
        return f"{self.producto} - {self.litros} L"

    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_litro
        self.subtotal = (Decimal(self.litros) * Decimal(self.precio_unitario)).quantize(Q2, rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)


class LogAccion(models.Model):
    usuario   = models.CharField(max_length=150, blank=True)
    evento    = models.CharField(max_length=20)  # CREATE, UPDATE, DELETE
    modelo    = models.CharField(max_length=50)
    pk_obj    = models.CharField(max_length=50)
    fecha_hora= models.DateTimeField(auto_now_add=True)
    payload   = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"{self.fecha_hora:%Y-%m-%d %H:%M} {self.evento} {self.modelo}({self.pk_obj})"

def _payload(instance):
    try:
        data = {}
        for f in instance._meta.fields:
            data[f.name] = str(getattr(instance, f.name))
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return ""

def _log(evento, instance):
    LogAccion.objects.create(
        usuario="",  
        evento=evento,
        modelo=instance.__class__.__name__,
        pk_obj=str(instance.pk or ""),
        payload=_payload(instance),
    )

@receiver(post_save, sender=Producto)
def _log_prod_save(sender, instance, created, **kwargs):
    _log("CREATE" if created else "UPDATE", instance)

@receiver(post_delete, sender=Producto)
def _log_prod_del(sender, instance, **kwargs):
    _log("DELETE", instance)

@receiver(post_save, sender=Cliente)
def _log_cli_save(sender, instance, created, **kwargs):
    _log("CREATE" if created else "UPDATE", instance)

@receiver(post_delete, sender=Cliente)
def _log_cli_del(sender, instance, **kwargs):
    _log("DELETE", instance)

@receiver(post_save, sender=Venta)
def _log_ven_save(sender, instance, created, **kwargs):
    _log("CREATE" if created else "UPDATE", instance)

@receiver(post_delete, sender=Venta)
def _log_ven_del(sender, instance, **kwargs):
    _log("DELETE", instance)
