from decimal import Decimal

from django.db import models, transaction

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=60, blank=True, default="")
    precio_litro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_litros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombres = models.CharField(max_length=120, default="")
    apellidos = models.CharField(max_length=120, blank=True, default="")
    telefono = models.CharField(max_length=30, blank=True, default="")
    nit = models.CharField(max_length=30, blank=True, default="CF")

    def __str__(self):
        return self.nombre_completo or "Cliente"

    @property
    def nombre_completo(self):
        nombres = (self.nombres or "").strip()
        apellidos = (self.apellidos or "").strip()
        return f"{nombres} {apellidos}".strip()


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ventas")
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.pk} - {self.cliente}"

    def confirmar(self):
        """Confirma la venta, actualizando existencias y el total."""
        with transaction.atomic():
            detalles = list(self.detalles.select_related("producto"))

            consumos = {}
            total = Decimal("0")

            for detalle in detalles:
                producto = detalle.producto
                litros = detalle.litros or Decimal("0")

                if litros <= 0:
                    continue

                if not detalle.precio_unitario:
                    detalle.precio_unitario = producto.precio_litro or Decimal("0")
                    detalle.save(update_fields=["precio_unitario"])

                total += litros * detalle.precio_unitario

                data = consumos.setdefault(producto.pk, {"producto": producto, "litros": Decimal("0")})
                data["litros"] += litros

            for data in consumos.values():
                producto = data["producto"]
                disponibles = producto.stock_litros or Decimal("0")
                if data["litros"] > disponibles:
                    raise ValueError(
                        f"Stock insuficiente para {producto.nombre}. Disponible: {disponibles}, solicitado: {data['litros']}"
                    )

            for data in consumos.values():
                producto = data["producto"]
                producto.stock_litros = (producto.stock_litros or Decimal("0")) - data["litros"]
                producto.save(update_fields=["stock_litros"])

            self.total = total
            self.save(update_fields=["total"])
            return total


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    litros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # <- se usa en ventas
  
