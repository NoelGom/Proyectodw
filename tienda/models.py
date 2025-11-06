from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=60, blank=True, default="")
    precio_por_litro = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # <- clave
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)            # <- clave
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=120, default="")   # <- existía el error de “nombre” faltante
    telefono = models.CharField(max_length=30, blank=True, default="")
    nit = models.CharField(max_length=30, blank=True, default="CF")

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ventas")
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.pk} - {self.cliente}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    litros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # <- se usa en ventas
  
