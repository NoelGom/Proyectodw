from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.utils import timezone

class Cliente(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30, blank=True)
    nit = models.CharField(max_length=20, blank=True)  # opcional
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
    nombre = models.CharField(max_length=120, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    precio_litro = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock_litros = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ventas")
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta #{self.pk or '—'} - {self.fecha:%Y-%m-%d %H:%M}"

    def recalcular_total(self):
        agg = sum((dv.subtotal for dv in self.detalles.all()), 0)
        self.total = agg
        return self.total

    @transaction.atomic
    def confirmar(self):
        """Confirma la venta: valida stock y descuenta."""
        # Validar stock
        for det in self.detalles.select_related("producto"):
            if det.litros <= 0:
                raise ValueError("Los litros deben ser mayores a 0.")
            if det.litros > det.producto.stock_litros:
                raise ValueError(f"Stock insuficiente para {det.producto.nombre}. Disponible: {det.producto.stock_litros} L.")
        # Descontar
        for det in self.detalles.select_related("producto"):
            prod = det.producto
            prod.stock_litros = prod.stock_litros - det.litros
            prod.save(update_fields=["stock_litros"])
        # Total
        self.recalcular_total()
        self.save(update_fields=["total"])


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    litros = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self):
        return f"{self.producto} - {self.litros} L"

    def save(self, *args, **kwargs):
        self.precio_unitario = self.precio_unitario or self.producto.precio_litro
        self.subtotal = (self.litros or 0) * (self.precio_unitario or 0)
        super().save(*args, **kwargs)
