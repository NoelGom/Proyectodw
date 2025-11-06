from django.db import models

TIPOS_PRODUCTO = [
    ('jabon', 'jabon'),
    ('desinfectante', 'desinfectante'),
    ('otro', 'otro'),
]

class Producto(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    tipo = models.CharField(max_length=30, choices=TIPOS_PRODUCTO)
   
    precio_por_litro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30, blank=True, default="")
    nit = models.CharField(max_length=30, blank=True, default="CF")

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.pk}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    litros = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return (self.litros or 0) * (self.precio_unitario or 0)
