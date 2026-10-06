import json
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps

from datetime import timedelta

from django.core.management import call_command
from django.db.models import F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from gestion.models import Categoria, Cliente, DetalleVenta, MovimientoCuenta, Producto, Proveedor, Usuario, Venta


def requiere_login(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not Usuario.objects.filter(id=request.session.get('usuario_id'), activo=True).exists():
            request.session.flush()
            return redirect('login')
        return vista(request, *args, **kwargs)
    return envoltura


def _contexto_base(request, seccion, titulo):
    usuario = Usuario.objects.filter(id=request.session.get('usuario_id')).first()
    return {'seccion': seccion, 'titulo': titulo, 'usuario': usuario}


def login_vista(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        usuario = Usuario.objects.filter(codigo=codigo, activo=True).first()
        if usuario:
            request.session['usuario_id'] = usuario.id
            request.session['usuario_rol'] = usuario.rol
            return redirect('venta')
        return render(request, 'login.html', {'error': 'Código incorrecto'})
    return render(request, 'login.html')


@requiere_login
def reiniciar_vista(request):
    call_command('cargar_demo')
    request.session.flush()
    return redirect('login')


def logout_vista(request):
    request.session.flush()
    return redirect('login')


@requiere_login
def venta_vista(request):
    return render(request, 'venta.html', _contexto_base(request, 'venta', 'Venta'))


def _saldo_de(cliente):
    ultimo = MovimientoCuenta.objects.filter(cliente=cliente).order_by('-fecha_movimiento', '-id').first()
    return (ultimo.saldo_nuevo if ultimo else Decimal('0')), ultimo


@requiere_login
def fiados_vista(request):
    filas = []
    total_por_cobrar = Decimal('0')
    for cliente in Cliente.objects.filter(activo=True):
        saldo, ultimo = _saldo_de(cliente)
        if saldo <= 0:
            continue
        total_por_cobrar += saldo
        filas.append({'cliente': cliente, 'saldo': saldo, 'ultimo': ultimo.fecha_movimiento if ultimo else None})
    filas.sort(key=lambda f: f['saldo'], reverse=True)
    contexto = _contexto_base(request, 'fiados', 'Fiados')
    contexto['filas'] = filas
    contexto['total_por_cobrar'] = total_por_cobrar
    return render(request, 'fiados.html', contexto)


@requiere_login
def fiado_detalle_vista(request, cliente_id):
    cliente = Cliente.objects.get(id=cliente_id)
    movimientos = MovimientoCuenta.objects.filter(cliente=cliente).select_related('venta').order_by('-fecha_movimiento', '-id')
    saldo, _ = _saldo_de(cliente)
    contexto = _contexto_base(request, 'fiados', cliente.nombre)
    contexto['cliente'] = cliente
    contexto['movimientos'] = movimientos
    contexto['saldo'] = saldo
    return render(request, 'fiado_detalle.html', contexto)


@csrf_exempt
@requiere_login
def abonar_api(request):
    datos = json.loads(request.body)
    cliente = Cliente.objects.get(id=datos['cliente_id'])
    valor = Decimal(str(datos['valor']))
    saldo_anterior, _ = _saldo_de(cliente)
    if valor <= 0 or valor > saldo_anterior:
        return JsonResponse({'error': 'Valor invalido'}, status=400)
    saldo_nuevo = saldo_anterior - valor
    MovimientoCuenta.objects.create(
        cliente=cliente,
        tipo=MovimientoCuenta.Tipo.ABONO,
        valor=valor,
        saldo_anterior=saldo_anterior,
        saldo_nuevo=saldo_nuevo,
        venta=None,
        fecha_movimiento=timezone.now(),
        observacion='Abono en efectivo',
    )
    return JsonResponse({'saldo_nuevo': str(saldo_nuevo)})


@requiere_login
def dashboard_vista(request):
    ahora = timezone.localtime()
    hoy = ahora.date()

    ventas_hoy = Venta.objects.filter(fecha__date=hoy).aggregate(total=Sum('total'))['total'] or Decimal('0')
    desde_semana = hoy - timedelta(days=6)
    ventas_semana = Venta.objects.filter(fecha__date__gte=desde_semana).aggregate(total=Sum('total'))['total'] or Decimal('0')

    total_por_cobrar = Decimal('0')
    for cliente in Cliente.objects.filter(activo=True):
        saldo, _ = _saldo_de(cliente)
        if saldo > 0:
            total_por_cobrar += saldo

    agotados = Producto.objects.filter(activo=True, stock__lte=0).count()
    limite_vencimiento = hoy + timedelta(days=20)
    por_vencer = Producto.objects.filter(
        activo=True, fecha_vencimiento__isnull=False,
        fecha_vencimiento__lte=limite_vencimiento, fecha_vencimiento__gte=hoy,
    ).count()

    por_dia = {
        fila['fecha__date']: fila['total']
        for fila in Venta.objects.filter(fecha__date__gte=desde_semana)
        .values('fecha__date').annotate(total=Sum('total'))
    }
    dias_es = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    barras = []
    for desplazamiento in range(6, -1, -1):
        dia = hoy - timedelta(days=desplazamiento)
        barras.append({'etiqueta': dias_es[dia.weekday()], 'fecha': dia, 'valor': por_dia.get(dia, Decimal('0'))})
    maximo = max([b['valor'] for b in barras] + [Decimal('1')])
    for barra in barras:
        barra['altura'] = int(barra['valor'] / maximo * 100)

    contexto = _contexto_base(request, 'dashboard', 'Dashboard')
    contexto.update({
        'ventas_hoy': ventas_hoy,
        'ventas_semana': ventas_semana,
        'total_por_cobrar': total_por_cobrar,
        'agotados': agotados,
        'por_vencer': por_vencer,
        'barras': barras,
    })
    return render(request, 'dashboard.html', contexto)


@requiere_login
def productos_vista(request):
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.filter(activo=True).select_related('categoria', 'proveedor')
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(marca__icontains=q) | Q(codigo_interno__icontains=q)
        )
    contexto = _contexto_base(request, 'productos', 'Productos')
    contexto['productos'] = productos.order_by('nombre')
    contexto['q'] = q
    contexto['categorias'] = Categoria.objects.filter(activa=True).order_by('nombre')
    contexto['proveedores'] = Proveedor.objects.filter(activo=True).order_by('nombre')
    return render(request, 'productos.html', contexto)


@csrf_exempt
@requiere_login
def producto_guardar_api(request):
    d = json.loads(request.body)
    campos = {
        'codigo_interno': d['codigo_interno'],
        'codigo_barras': d.get('codigo_barras') or None,
        'nombre': d['nombre'],
        'marca': d.get('marca', ''),
        'categoria_id': d['categoria_id'],
        'tipo_venta': d['tipo_venta'],
        'unidad_medida': 'KG' if d['tipo_venta'] == Producto.TipoVenta.PESO else 'UND',
        'precio_compra': Decimal(str(d['precio_compra'])),
        'precio_venta': Decimal(str(d['precio_venta'])),
        'stock': Decimal(str(d['stock'])),
        'stock_minimo': Decimal(str(d['stock_minimo'])),
        'proveedor_id': d.get('proveedor_id') or None,
        'fecha_vencimiento': d.get('fecha_vencimiento') or None,
    }
    producto_id = d.get('id')
    if producto_id:
        Producto.objects.filter(id=producto_id).update(**campos)
    else:
        if Producto.objects.filter(codigo_interno=campos['codigo_interno']).exists():
            return JsonResponse({'error': 'Ese código interno ya existe'}, status=400)
        Producto.objects.create(activo=True, **campos)
    return JsonResponse({'ok': True})


@csrf_exempt
@requiere_login
def producto_eliminar_api(request):
    d = json.loads(request.body)
    Producto.objects.filter(id=d['id']).update(activo=False)
    return JsonResponse({'ok': True})


@csrf_exempt
@requiere_login
def cliente_guardar_api(request):
    d = json.loads(request.body)
    cliente = Cliente.objects.create(
        nombre=d['nombre'],
        documento=d.get('documento', ''),
        telefono=d.get('telefono', ''),
        direccion=d.get('direccion', ''),
        limite_credito=Decimal(str(d.get('limite_credito') or 500000)),
        activo=True,
    )
    return JsonResponse({'id': cliente.id, 'nombre': cliente.nombre})


@requiere_login
def inventario_vista(request):
    agotados = Producto.objects.filter(activo=True, stock__lte=0).select_related('categoria', 'proveedor').order_by('nombre')
    bajo_minimo = Producto.objects.filter(
        activo=True, stock__gt=0, stock__lt=F('stock_minimo')
    ).select_related('categoria', 'proveedor').order_by('nombre')
    contexto = _contexto_base(request, 'inventario', 'Inventario bajo')
    contexto['agotados'] = agotados
    contexto['bajo_minimo'] = bajo_minimo
    return render(request, 'inventario.html', contexto)


@requiere_login
def buscar_api(request):
    q = request.GET.get('q', '').strip()
    exacto = False
    productos = []

    if q:
        coincidencia = Producto.objects.filter(activo=True).filter(
            Q(codigo_barras=q) | Q(codigo_interno=q)
        ).first()
        if coincidencia:
            exacto = True
            productos = [coincidencia]
        else:
            productos = list(Producto.objects.filter(activo=True, nombre__icontains=q)[:8])

    data = {
        'resultados': [
            {
                'id': producto.id,
                'codigo_interno': producto.codigo_interno,
                'nombre': producto.nombre,
                'marca': producto.marca,
                'precio_venta': str(producto.precio_venta),
                'tipo_venta': producto.tipo_venta,
                'unidad_medida': producto.unidad_medida,
                'stock': str(producto.stock),
            }
            for producto in productos
        ]
    }
    if exacto:
        data['exacto'] = True
    return JsonResponse(data)


@csrf_exempt
@requiere_login
def vender_api(request):
    datos = json.loads(request.body)
    items = datos.get('items', [])
    metodo_pago = datos.get('metodo_pago')
    cliente_id = datos.get('cliente_id')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    cliente = Cliente.objects.filter(id=cliente_id).first() if cliente_id else None

    detalles_info = []
    subtotal_venta = Decimal('0')
    for item in items:
        producto = Producto.objects.get(id=item['producto_id'])
        cantidad = Decimal(str(item['cantidad']))
        precio_unitario = producto.precio_venta
        costo_unitario = producto.precio_compra
        subtotal_detalle = cantidad * precio_unitario
        subtotal_venta += subtotal_detalle
        detalles_info.append((producto, cantidad, precio_unitario, costo_unitario, subtotal_detalle))

    total_venta = (subtotal_venta / Decimal('50')).to_integral_value(rounding=ROUND_HALF_UP) * Decimal('50')
    tipo_venta = Venta.TipoVenta.CREDITO if metodo_pago == Venta.MetodoPago.FIADO else Venta.TipoVenta.CONTADO

    ultima_venta = Venta.objects.order_by('-id').first()
    siguiente_numero = int(ultima_venta.numero.split('-')[1]) + 1 if ultima_venta else 1
    numero = f'V-{siguiente_numero:05d}'

    venta = Venta.objects.create(
        numero=numero,
        fecha=timezone.now(),
        usuario=usuario,
        cliente=cliente,
        subtotal=subtotal_venta,
        total=total_venta,
        metodo_pago=metodo_pago,
        tipo_venta=tipo_venta,
        estado='COMPLETADA',
    )

    items_comprobante = []
    for producto, cantidad, precio_unitario, costo_unitario, subtotal_detalle in detalles_info:
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            costo_unitario=costo_unitario,
            subtotal=subtotal_detalle,
        )
        producto.stock = producto.stock - cantidad
        producto.save()
        items_comprobante.append({
            'nombre': producto.nombre,
            'cantidad': str(cantidad),
            'precio_unitario': str(precio_unitario),
            'subtotal': str(subtotal_detalle),
        })

    saldo_nuevo = None
    if metodo_pago == Venta.MetodoPago.FIADO:
        ultimo_movimiento = MovimientoCuenta.objects.filter(cliente=cliente).order_by('-fecha_movimiento', '-id').first()
        saldo_anterior = ultimo_movimiento.saldo_nuevo if ultimo_movimiento else Decimal('0')
        saldo_nuevo = saldo_anterior + total_venta
        MovimientoCuenta.objects.create(
            cliente=cliente,
            tipo=MovimientoCuenta.Tipo.CARGO,
            valor=total_venta,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            venta=venta,
            fecha_movimiento=venta.fecha,
            observacion='',
        )

    comprobante = {
        'numero': venta.numero,
        'fecha': timezone.localtime(venta.fecha).strftime('%d/%m/%Y %H:%M'),
        'items': items_comprobante,
        'subtotal': str(subtotal_venta),
        'total': str(total_venta),
        'metodo_pago': metodo_pago,
        'cliente_nombre': cliente.nombre if cliente else None,
        'saldo_nuevo': str(saldo_nuevo) if saldo_nuevo is not None else None,
        'usuario_nombre': usuario.nombre,
    }
    return JsonResponse(comprobante)


@requiere_login
def clientes_api(request):
    clientes = []
    for cliente in Cliente.objects.filter(activo=True):
        ultimo = MovimientoCuenta.objects.filter(cliente=cliente).order_by('-fecha_movimiento', '-id').first()
        saldo = ultimo.saldo_nuevo if ultimo else Decimal('0')
        clientes.append({'id': cliente.id, 'nombre': cliente.nombre, 'saldo': str(saldo)})
    return JsonResponse({'clientes': clientes})
