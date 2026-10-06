import random
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand
from django.utils import timezone

from gestion.models import (
    Usuario,
    Categoria,
    Proveedor,
    Producto,
    Cliente,
    Venta,
    DetalleVenta,
    MovimientoCuenta,
)


class Command(BaseCommand):
    help = 'Carga datos demo para Danna'

    def handle(self, *args, **options):
        random.seed(2026)

        DetalleVenta.objects.all().delete()
        MovimientoCuenta.objects.all().delete()
        Venta.objects.all().delete()
        Producto.objects.all().delete()
        Cliente.objects.all().delete()
        Proveedor.objects.all().delete()
        Categoria.objects.all().delete()
        Usuario.objects.all().delete()

        carlos = Usuario.objects.create(codigo='1234', nombre='Carlos Danna', rol=Usuario.Rol.ADMIN, activo=True)
        yesenia = Usuario.objects.create(codigo='5678', nombre='Yesenia Rojas', rol=Usuario.Rol.CAJERO, activo=True)
        usuarios = [carlos, yesenia]

        proveedores_data = [
            ('Distribuidora El Progreso', '3154829017', 'Marta Gómez'),
            ('Surtitienda Santander', '3108472916', 'Rafael Niño'),
            ('Lácteos del Oriente', '3192756148', 'Omar Pinzón'),
            ('Comercializadora La 15', '3047182639', 'Diana Lozano'),
        ]
        proveedores = [
            Proveedor.objects.create(nombre=nombre, telefono=telefono, contacto=contacto, activo=True)
            for nombre, telefono, contacto in proveedores_data
        ]

        categorias_nombres = [
            'Granos y cereales', 'Aceites y grasas', 'Enlatados', 'Lácteos',
            'Carnes y embutidos', 'Frutas y verduras', 'Panadería', 'Bebidas',
            'Gaseosas y jugos', 'Licores', 'Confitería', 'Snacks', 'Café y chocolate',
            'Condimentos y salsas', 'Aseo del hogar', 'Cuidado personal',
            'Papelería', 'Mascotas', 'Varios',
        ]
        categorias = {nombre: Categoria.objects.create(nombre=nombre, activa=True) for nombre in categorias_nombres}

        productos_data = [
            ('P001', 'Arroz Diana 500g', 'Diana', 'Granos y cereales', Producto.TipoVenta.UNIDAD, 2100, 2800, '48', '15'),
            ('P002', 'Arroz Diana 1000g', 'Diana', 'Granos y cereales', Producto.TipoVenta.UNIDAD, 4000, 5200, '32', '12'),
            ('P003', 'Lenteja 500g', 'Del Monte', 'Granos y cereales', Producto.TipoVenta.UNIDAD, 2600, 3500, '20', '10'),
            ('P004', 'Fríjol cargamanto 500g', 'La Nutresa', 'Granos y cereales', Producto.TipoVenta.UNIDAD, 4200, 5500, '8', '10'),
            ('P005', 'Pasta espagueti 250g', 'Doria', 'Granos y cereales', Producto.TipoVenta.UNIDAD, 1900, 2600, '40', '15'),
            ('P006', 'Aceite Premier 1000ml', 'Premier', 'Aceites y grasas', Producto.TipoVenta.UNIDAD, 7800, 9800, '24', '10'),
            ('P007', 'Aceite Gourmet 3000ml', 'Gourmet', 'Aceites y grasas', Producto.TipoVenta.UNIDAD, 22000, 27500, '6', '5'),
            ('P008', 'Margarina Rama 250g', 'Rama', 'Aceites y grasas', Producto.TipoVenta.UNIDAD, 3400, 4400, '15', '8'),
            ('P009', 'Atún Van Camps 160g', 'Van Camps', 'Enlatados', Producto.TipoVenta.UNIDAD, 4900, 6300, '36', '12'),
            ('P010', 'Sardina Van Camps 425g', 'Van Camps', 'Enlatados', Producto.TipoVenta.UNIDAD, 6200, 7900, '0', '8'),
            ('P011', 'Leche Colanta 1000ml', 'Colanta', 'Lácteos', Producto.TipoVenta.UNIDAD, 3600, 4600, '28', '15'),
            ('P012', 'Leche en polvo Klim 380g', 'Klim', 'Lácteos', Producto.TipoVenta.UNIDAD, 17500, 21500, '9', '6'),
            ('P013', 'Queso campesino 500g', 'Colanta', 'Lácteos', Producto.TipoVenta.UNIDAD, 9500, 12000, '7', '5'),
            ('P014', 'Yogurt Alpina 1000g', 'Alpina', 'Lácteos', Producto.TipoVenta.UNIDAD, 6800, 8500, '12', '6'),
            ('P015', 'Huevos AA x30', 'Santa Reyes', 'Lácteos', Producto.TipoVenta.UNIDAD, 16500, 20000, '14', '8'),
            ('P016', 'Salchichón cervecero 500g', 'Zenú', 'Carnes y embutidos', Producto.TipoVenta.UNIDAD, 11000, 14000, '5', '6'),
            ('P017', 'Salchicha Ranchera 450g', 'Zenú', 'Carnes y embutidos', Producto.TipoVenta.UNIDAD, 9800, 12500, '11', '6'),
            ('P018', 'Mortadela 250g', 'Rica', 'Carnes y embutidos', Producto.TipoVenta.UNIDAD, 4200, 5500, '0', '5'),
            ('P019', 'Papa pastusa', 'Granel', 'Frutas y verduras', Producto.TipoVenta.PESO, 2200, 3200, '85.5', '20'),
            ('P020', 'Cebolla cabezona', 'Granel', 'Frutas y verduras', Producto.TipoVenta.PESO, 2800, 4000, '42.3', '15'),
            ('P021', 'Tomate chonto', 'Granel', 'Frutas y verduras', Producto.TipoVenta.PESO, 3000, 4500, '18.7', '20'),
            ('P022', 'Yuca', 'Granel', 'Frutas y verduras', Producto.TipoVenta.PESO, 1800, 2800, '30.2', '15'),
            ('P023', 'Plátano hartón', 'Granel', 'Frutas y verduras', Producto.TipoVenta.PESO, 2400, 3600, '55.8', '20'),
            ('P024', 'Zanahoria', 'Granel', 'Frutas y verduras', Producto.TipoVenta.PESO, 2000, 3000, '12.4', '15'),
            ('P025', 'Limón Tahití', 'Granel', 'Frutas y verduras', Producto.TipoVenta.PESO, 3500, 5000, '8.6', '10'),
            ('P026', 'Pan tajado Bimbo 450g', 'Bimbo', 'Panadería', Producto.TipoVenta.UNIDAD, 5800, 7200, '10', '6'),
            ('P027', 'Panela redonda 500g', 'La Dulzura', 'Panadería', Producto.TipoVenta.UNIDAD, 2800, 3800, '45', '15'),
            ('P028', 'Agua Cristal 600ml', 'Cristal', 'Bebidas', Producto.TipoVenta.UNIDAD, 1400, 2000, '60', '24'),
            ('P029', 'Coca-Cola 400ml', 'Coca-Cola', 'Gaseosas y jugos', Producto.TipoVenta.UNIDAD, 1900, 2800, '72', '24'),
            ('P030', 'Coca-Cola 1500ml', 'Coca-Cola', 'Gaseosas y jugos', Producto.TipoVenta.UNIDAD, 4300, 5800, '30', '12'),
            ('P031', 'Postobón Manzana 400ml', 'Postobón', 'Gaseosas y jugos', Producto.TipoVenta.UNIDAD, 1800, 2600, '48', '24'),
            ('P032', 'Jugo Hit 500ml', 'Hit', 'Gaseosas y jugos', Producto.TipoVenta.UNIDAD, 2200, 3200, '3', '12'),
            ('P033', 'Cerveza Águila 330ml', 'Águila', 'Licores', Producto.TipoVenta.UNIDAD, 2600, 3800, '96', '24'),
            ('P034', 'Aguardiente Néctar 750ml', 'Néctar', 'Licores', Producto.TipoVenta.UNIDAD, 38000, 47000, '8', '4'),
            ('P035', 'Bon Bon Bum', 'Colombina', 'Confitería', Producto.TipoVenta.UNIDAD, 400, 700, '150', '50'),
            ('P036', 'Chocolatina Jet', 'Jet', 'Confitería', Producto.TipoVenta.UNIDAD, 900, 1400, '80', '30'),
            ('P037', 'Papas Margarita 105g', 'Margarita', 'Snacks', Producto.TipoVenta.UNIDAD, 3600, 4800, '25', '12'),
            ('P038', 'Café Sello Rojo 250g', 'Sello Rojo', 'Café y chocolate', Producto.TipoVenta.UNIDAD, 7500, 9500, '18', '8'),
            ('P039', 'Chocolate Corona 250g', 'Corona', 'Café y chocolate', Producto.TipoVenta.UNIDAD, 5200, 6800, '14', '8'),
            ('P040', 'Sal refisal 500g', 'Refisal', 'Condimentos y salsas', Producto.TipoVenta.UNIDAD, 1200, 1800, '35', '12'),
            ('P041', 'Salsa de tomate Fruco 200g', 'Fruco', 'Condimentos y salsas', Producto.TipoVenta.UNIDAD, 3200, 4300, '2', '8'),
            ('P042', 'Jabón Rey barra 300g', 'Rey', 'Aseo del hogar', Producto.TipoVenta.UNIDAD, 2400, 3300, '40', '15'),
            ('P043', 'Detergente Fab 900g', 'Fab', 'Aseo del hogar', Producto.TipoVenta.UNIDAD, 8500, 10800, '16', '8'),
            ('P044', 'Papel higiénico Familia x4', 'Familia', 'Aseo del hogar', Producto.TipoVenta.UNIDAD, 7200, 9200, '22', '10'),
            ('P045', 'Crema dental Colgate 100ml', 'Colgate', 'Cuidado personal', Producto.TipoVenta.UNIDAD, 4800, 6200, '0', '8'),
            ('P046', 'Cuaderno cuadriculado 100h', 'Norma', 'Papelería', Producto.TipoVenta.UNIDAD, 3500, 4800, '28', '10'),
        ]

        hoy = timezone.localdate()
        vencimientos = {'P011': 3, 'P013': 7, 'P014': 11, 'P017': 15, 'P026': 19}

        productos = []
        for indice, (codigo_interno, nombre, marca, categoria_nombre, tipo_venta, precio_compra, precio_venta, stock, stock_minimo) in enumerate(productos_data, start=1):
            if tipo_venta == Producto.TipoVenta.UNIDAD:
                unidad_medida = 'UND'
                codigo_barras = f'77{indice:011d}'
            else:
                unidad_medida = 'KG'
                codigo_barras = None

            offset = vencimientos.get(codigo_interno)
            fecha_vencimiento = hoy + timedelta(days=offset) if offset else None

            producto = Producto.objects.create(
                codigo_barras=codigo_barras,
                codigo_interno=codigo_interno,
                nombre=nombre,
                categoria=categorias[categoria_nombre],
                marca=marca,
                tipo_venta=tipo_venta,
                unidad_medida=unidad_medida,
                precio_compra=Decimal(precio_compra),
                precio_venta=Decimal(precio_venta),
                stock=Decimal(stock),
                stock_minimo=Decimal(stock_minimo),
                proveedor=proveedores[(indice - 1) % len(proveedores)],
                fecha_vencimiento=fecha_vencimiento,
                activo=True,
            )
            productos.append(producto)

        clientes_data = [
            ('María Elena Rueda Serrano', '63482917', '3152847391', 'Calle 5 # 3-24', 285000),
            ('José Gregorio Patiño Ortiz', '91347582', '3104729183', 'Carrera 8 # 12-10', 142000),
            ('Blanca Nubia Acevedo Díaz', '37829154', '3187264910', 'Calle 10 # 4-56', 398000),
            ('Luis Alberto Carreño Mantilla', '13849267', '3002948175', 'Carrera 3 # 9-18', 96000),
            ('Rosalba Jaimes Villamizar', '28174639', '3145829037', 'Calle 7 # 6-33', 217000),
            ('Hernán Darío Prada Gómez', '91028473', '3209471628', 'Carrera 11 # 2-45', 173000),
            ('Gladys Esperanza Moreno Sepúlveda', '63719482', '3116284759', 'Calle 4 # 8-12', 324000),
            ('Álvaro Antonio Ochoa Flórez', '13572948', '3058392746', 'Carrera 6 # 15-20', 88000),
            ('Yolanda Cristina Bautista Rangel', '37914628', '3192837465', 'Calle 9 # 1-07', 256000),
            ('Pedro Nel Suárez Camacho', '91738264', '3024758193', 'Carrera 2 # 10-30', 131000),
        ]

        clientes_info = []
        for nombre, documento, telefono, direccion, saldo_objetivo in clientes_data:
            cliente = Cliente.objects.create(
                nombre=nombre,
                documento=documento,
                telefono=telefono,
                direccion=direccion,
                limite_credito=Decimal('500000'),
                activo=True,
            )
            clientes_info.append((cliente, Decimal(str(saldo_objetivo))))

        random.shuffle(clientes_info)

        def redondear_50(valor):
            return (valor / Decimal('50')).to_integral_value(rounding=ROUND_HALF_UP) * Decimal('50')

        def generar_hora():
            r = random.random()
            if r < 0.35:
                minutos = int(random.gauss(11 * 60, 70))
            elif r < 0.70:
                minutos = int(random.gauss(18 * 60, 80))
            else:
                minutos = random.randint(7 * 60, 20 * 60 - 1)
            minutos = max(7 * 60, min(20 * 60 - 1, minutos))
            return time(minutos // 60, minutos % 60)

        metodo_pago_opciones = (
            [Venta.MetodoPago.EFECTIVO] * 45
            + [Venta.MetodoPago.NEQUI] * 20
            + [Venta.MetodoPago.DAVIPLATA] * 12
            + [Venta.MetodoPago.FIADO] * 18
            + [Venta.MetodoPago.TARJETA] * 5
        )

        fecha_inicio = hoy - timedelta(days=27)
        dias = [fecha_inicio + timedelta(days=i) for i in range(28)]

        cargos_por_cliente = {cliente.id: [] for cliente, _ in clientes_info}
        indice_fiado = 0
        indice_venta = 0

        for dia in dias:
            dia_semana = dia.weekday()
            if dia_semana <= 3:
                n_ventas = random.randint(25, 40)
            elif dia_semana == 4:
                n_ventas = random.randint(45, 60)
            elif dia_semana == 5:
                n_ventas = random.randint(60, 80)
            else:
                n_ventas = random.randint(50, 65)

            for _ in range(n_ventas):
                indice_venta += 1
                fecha_hora = timezone.make_aware(datetime.combine(dia, generar_hora()))
                cantidad_productos = random.randint(1, 7)
                productos_venta = random.sample(productos, cantidad_productos)

                detalles = []
                subtotal_venta = Decimal('0')
                for producto in productos_venta:
                    if producto.tipo_venta == Producto.TipoVenta.UNIDAD:
                        cantidad = Decimal(random.randint(1, 4))
                    else:
                        cantidad = Decimal(str(round(random.uniform(0.3, 3.5), 3)))
                    precio_unitario = producto.precio_venta
                    costo_unitario = producto.precio_compra
                    subtotal_detalle = cantidad * precio_unitario
                    subtotal_venta += subtotal_detalle
                    detalles.append((producto, cantidad, precio_unitario, costo_unitario, subtotal_detalle))

                metodo_pago = random.choice(metodo_pago_opciones)
                if metodo_pago == Venta.MetodoPago.FIADO:
                    tipo_venta = Venta.TipoVenta.CREDITO
                    cliente = clientes_info[indice_fiado % len(clientes_info)][0]
                    indice_fiado += 1
                else:
                    tipo_venta = Venta.TipoVenta.CONTADO
                    cliente = None

                total_venta = redondear_50(subtotal_venta)
                usuario = usuarios[indice_venta % 2]

                venta = Venta.objects.create(
                    numero=f'V-{indice_venta:05d}',
                    fecha=fecha_hora,
                    usuario=usuario,
                    cliente=cliente,
                    subtotal=subtotal_venta,
                    total=total_venta,
                    metodo_pago=metodo_pago,
                    tipo_venta=tipo_venta,
                    estado='COMPLETADA',
                )

                for producto, cantidad, precio_unitario, costo_unitario, subtotal_detalle in detalles:
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        costo_unitario=costo_unitario,
                        subtotal=subtotal_detalle,
                    )

                if metodo_pago == Venta.MetodoPago.FIADO:
                    cargos_por_cliente[cliente.id].append((fecha_hora, total_venta, venta))

        total_por_cobrar = Decimal('0')
        techo_fiado = Decimal('250000')

        for cliente, saldo_objetivo in clientes_info:
            cargos = sorted(cargos_por_cliente[cliente.id], key=lambda c: c[0])
            eventos = []
            saldo = Decimal('0')

            for indice, (fecha, valor, venta) in enumerate(cargos):
                eventos.append((fecha, MovimientoCuenta.Tipo.CARGO, valor, venta, ''))
                saldo += valor
                if saldo > techo_fiado and indice < len(cargos) - 1:
                    porcentaje = Decimal(str(round(random.uniform(0.4, 0.8), 2)))
                    valor_abono = (saldo * porcentaje).quantize(Decimal('1'))
                    if valor_abono > 0:
                        margen = int((cargos[indice + 1][0] - fecha).total_seconds() // 60) - 1
                        if margen > 1:
                            fecha_abono = fecha + timedelta(minutes=random.randint(1, min(margen, 2880)))
                            eventos.append((fecha_abono, MovimientoCuenta.Tipo.ABONO, valor_abono, None, 'Abono en efectivo'))
                            saldo -= valor_abono

            ultima_fecha = eventos[-1][0] if eventos else timezone.make_aware(datetime.combine(hoy, time(19, 0)))
            diferencia = saldo - saldo_objetivo
            if diferencia > 0:
                eventos.append((ultima_fecha + timedelta(minutes=random.randint(30, 240)), MovimientoCuenta.Tipo.ABONO, diferencia, None, 'Abono en efectivo'))
            elif diferencia < 0:
                eventos.append((ultima_fecha + timedelta(minutes=random.randint(30, 240)), MovimientoCuenta.Tipo.CARGO, -diferencia, None, 'Fiado'))

            saldo = Decimal('0')
            for fecha, tipo, valor, venta, observacion in eventos:
                saldo_anterior = saldo
                if tipo == MovimientoCuenta.Tipo.CARGO:
                    saldo_nuevo = saldo_anterior + valor
                else:
                    saldo_nuevo = saldo_anterior - valor
                MovimientoCuenta.objects.create(
                    cliente=cliente,
                    tipo=tipo,
                    valor=valor,
                    saldo_anterior=saldo_anterior,
                    saldo_nuevo=saldo_nuevo,
                    venta=venta,
                    fecha_movimiento=fecha,
                    observacion=observacion,
                )
                saldo = saldo_nuevo

            total_por_cobrar += saldo

        self.stdout.write(self.style.SUCCESS('Resumen de carga demo'))
        self.stdout.write(f'Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'Productos: {Producto.objects.count()}')
        self.stdout.write(f'Clientes: {Cliente.objects.count()}')
        self.stdout.write(f'Ventas: {Venta.objects.count()}')
        self.stdout.write(f'Detalles de venta: {DetalleVenta.objects.count()}')
        self.stdout.write(f'Movimientos de cuenta: {MovimientoCuenta.objects.count()}')
        self.stdout.write(f'Total por cobrar: {total_por_cobrar}')
