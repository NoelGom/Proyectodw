from django.test import TestCase
from decimal import Decimal
from .models import Producto, Cliente, Venta, DetalleVenta

class VentaTests(TestCase):
    def setUp(self):
        self.cli = Cliente.objects.create(nombres="Juan", apellidos="Pérez")
        self.prod = Producto.objects.create(nombre="Jabón Azul", tipo="jabon", precio_litro=Decimal("10.00"), stock_litros=Decimal("50"))

    def test_crear_venta_descuenta_stock(self):
        v = Venta.objects.create(cliente=self.cli)
        DetalleVenta.objects.create(venta=v, producto=self.prod, litros=Decimal("3.00"), precio_unitario=Decimal("10.00"))
        v.confirmar()
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.stock_litros, Decimal("47.00"))
        self.assertEqual(v.total, Decimal("30.00"))

    def test_evitar_sobreventa(self):
        v = Venta.objects.create(cliente=self.cli)
        DetalleVenta.objects.create(venta=v, producto=self.prod, litros=Decimal("60.00"), precio_unitario=Decimal("10.00"))
        with self.assertRaises(ValueError):
            v.confirmar()
