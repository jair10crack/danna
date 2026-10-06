from django.db import models


class Usuario(models.Model):
    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        CAJERO = 'CAJERO', 'Cajero'

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    rol = models.CharField(max_length=10, choices=Rol.choices)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    contacto = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class TipoVenta(models.TextChoices):
        UNIDAD = 'UNIDAD', 'Unidad'
        PESO = 'PESO', 'Peso'

    codigo_barras = models.CharField(max_length=50, unique=True, null=True, blank=True)
    codigo_interno = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100)
    tipo_venta = models.CharField(max_length=10, choices=TipoVenta.choices)
    unidad_medida = models.CharField(max_length=20)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.DecimalField(max_digits=10, decimal_places=3)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=3)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.codigo_interno} - {self.nombre}'


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    documento = models.CharField(max_length=30)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    limite_credito = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        NEQUI = 'NEQUI', 'Nequi'
        DAVIPLATA = 'DAVIPLATA', 'Daviplata'
        TARJETA = 'TARJETA', 'Tarjeta'
        FIADO = 'FIADO', 'Fiado'

    class TipoVenta(models.TextChoices):
        CONTADO = 'CONTADO', 'Contado'
        CREDITO = 'CREDITO', 'Credito'

    numero = models.CharField(max_length=30, unique=True)
    fecha = models.DateTimeField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)
    tipo_venta = models.CharField(max_length=10, choices=TipoVenta.choices)
    estado = models.CharField(max_length=20)

    def __str__(self):
        return self.numero


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.venta} - {self.producto}'


class MovimientoCuenta(models.Model):
    class Tipo(models.TextChoices):
        CARGO = 'CARGO', 'Cargo'
        ABONO = 'ABONO', 'Abono'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_nuevo = models.DecimalField(max_digits=12, decimal_places=2)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, null=True, blank=True)
    fecha_movimiento = models.DateTimeField()
    observacion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.cliente} - {self.tipo}'
