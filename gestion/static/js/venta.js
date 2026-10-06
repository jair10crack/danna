(function () {
    const buscador = document.getElementById('buscador');
    const resultadosDiv = document.getElementById('resultados-busqueda');
    const tablaVenta = document.getElementById('tabla-venta');
    const cuerpoVenta = document.getElementById('cuerpo-venta');
    const ventaVacia = document.getElementById('venta-vacia');
    const totalNumero = document.getElementById('total-numero');
    const subtotalChico = document.getElementById('subtotal-chico');
    const botonesMetodo = Array.from(document.querySelectorAll('.boton-metodo'));
    const bloqueCliente = document.getElementById('bloque-cliente');
    const selectCliente = document.getElementById('select-cliente');
    const saldoActual = document.getElementById('saldo-actual');
    const botonCobrar = document.getElementById('boton-cobrar');
    const overlayComprobante = document.getElementById('overlay-comprobante');
    const comprobanteInfo = document.getElementById('comprobante-info');
    const comprobanteItems = document.getElementById('comprobante-items');
    const comprobanteTotal = document.getElementById('comprobante-total');
    const comprobanteMetodo = document.getElementById('comprobante-metodo');
    const comprobanteSaldo = document.getElementById('comprobante-saldo');
    const botonNuevaVenta = document.getElementById('boton-nueva-venta');

    let items = [];
    let metodoPago = null;
    let clienteId = null;
    let resultadosActuales = [];
    let indiceSeleccionado = -1;
    let temporizadorBusqueda = null;

    function formatearPesos(valor) {
        const entero = Math.round(valor || 0);
        return '$' + entero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function formatearCantidad(valor) {
        const numero = parseFloat(valor) || 0;
        return Number.isInteger(numero) ? numero.toString() : numero.toFixed(3).replace(/0+$/, '').replace('.', ',');
    }

    function redondear50(valor) {
        return Math.round(valor / 50) * 50;
    }

    function ocultarResultados() {
        resultadosDiv.classList.add('oculto');
        resultadosDiv.innerHTML = '';
        resultadosActuales = [];
        indiceSeleccionado = -1;
    }

    function resaltarSeleccion() {
        resultadosDiv.querySelectorAll('.resultado-item').forEach((el, i) => {
            el.classList.toggle('seleccionado', i === indiceSeleccionado);
        });
    }

    function mostrarResultados(resultados) {
        resultadosActuales = resultados;
        indiceSeleccionado = -1;
        if (resultados.length === 0) {
            ocultarResultados();
            return;
        }
        resultadosDiv.innerHTML = resultados.map((r, i) => {
            const existencia = parseFloat(r.stock) || 0;
            const claseStock = existencia <= 0 ? 'stock-agotado' : 'stock-normal';
            const textoStock = existencia <= 0 ? 'Agotado' : formatearCantidad(r.stock) + ' ' + r.unidad_medida;
            return `
            <div class="resultado-item" data-indice="${i}">
                <span class="resultado-nombre">${r.nombre} <span class="resultado-marca">${r.marca}</span></span>
                <span class="resultado-derecha">
                    <span class="resultado-stock ${claseStock}">${textoStock}</span>
                    <span class="plata resultado-precio">${formatearPesos(parseFloat(r.precio_venta))}</span>
                </span>
            </div>`;
        }).join('');
        resultadosDiv.classList.remove('oculto');
    }

    function buscar(q) {
        fetch(`/api/buscar/?q=${encodeURIComponent(q)}`)
            .then(r => r.json())
            .then(data => {
                if (data.exacto && data.resultados.length) {
                    agregarProducto(data.resultados[0]);
                } else {
                    mostrarResultados(data.resultados);
                }
            });
    }

    function agregarProducto(producto) {
        const id = producto.id;
        if (producto.tipo_venta === 'UNIDAD') {
            const existente = items.find(i => i.id === id);
            if (existente) {
                existente.cantidad += 1;
            } else {
                items.push({
                    id: id,
                    nombre: producto.nombre,
                    precio_unitario: parseFloat(producto.precio_venta),
                    cantidad: 1,
                    tipo_venta: producto.tipo_venta,
                });
            }
            renderTabla();
            buscador.value = '';
            ocultarResultados();
            buscador.focus();
        } else {
            if (!items.find(i => i.id === id)) {
                items.push({
                    id: id,
                    nombre: producto.nombre,
                    precio_unitario: parseFloat(producto.precio_venta),
                    cantidad: '',
                    tipo_venta: producto.tipo_venta,
                });
                renderTabla();
            }
            buscador.value = '';
            ocultarResultados();
            const input = cuerpoVenta.querySelector(`input[data-id="${id}"]`);
            if (input) {
                input.focus();
                input.select();
            }
        }
    }

    function renderTabla() {
        cuerpoVenta.innerHTML = '';
        if (items.length === 0) {
            tablaVenta.classList.add('oculto');
            ventaVacia.classList.remove('oculto');
        } else {
            tablaVenta.classList.remove('oculto');
            ventaVacia.classList.add('oculto');
            items.forEach(item => {
                const fila = document.createElement('tr');
                const subtotalItem = (parseFloat(item.cantidad) || 0) * item.precio_unitario;
                fila.innerHTML = `
                    <td>${item.nombre}</td>
                    <td><input type="text" class="input-cantidad" data-id="${item.id}" value="${item.cantidad}"></td>
                    <td class="plata">${formatearPesos(item.precio_unitario)}</td>
                    <td class="plata">${formatearPesos(subtotalItem)}</td>
                    <td><span class="quitar-fila" data-id="${item.id}">&times;</span></td>
                `;
                cuerpoVenta.appendChild(fila);
            });
        }
        calcularTotales();
    }

    function calcularTotales() {
        const subtotal = items.reduce((acc, i) => acc + (parseFloat(i.cantidad) || 0) * i.precio_unitario, 0);
        const total = redondear50(subtotal);
        totalNumero.textContent = formatearPesos(total);
        if (Math.round(total) !== Math.round(subtotal)) {
            subtotalChico.textContent = formatearPesos(subtotal);
            subtotalChico.classList.remove('oculto');
        } else {
            subtotalChico.classList.add('oculto');
        }
    }

    function elegirMetodo(metodo) {
        metodoPago = metodo;
        botonesMetodo.forEach(btn => btn.classList.toggle('elegido', btn.dataset.metodo === metodo));
        if (metodo === 'FIADO') {
            bloqueCliente.classList.remove('oculto');
            cargarClientes();
        } else {
            bloqueCliente.classList.add('oculto');
            clienteId = null;
        }
    }

    function actualizarSaldoActual() {
        const opcion = selectCliente.selectedOptions[0];
        if (opcion && selectCliente.value) {
            saldoActual.textContent = 'Saldo actual: ' + formatearPesos(parseFloat(opcion.dataset.saldo));
        } else {
            saldoActual.textContent = '';
        }
    }

    function cargarClientes() {
        return fetch('/api/clientes/')
            .then(r => r.json())
            .then(data => {
                selectCliente.innerHTML = '<option value="">Seleccione un cliente</option>' +
                    data.clientes.map(c => `<option value="${c.id}" data-saldo="${c.saldo}">${c.nombre}</option>`).join('');
                actualizarSaldoActual();
            });
    }

    function cobrar() {
        if (items.length === 0) return;
        if (metodoPago === 'FIADO' && !clienteId) return;
        if (!metodoPago) return;

        const payload = {
            items: items.map(i => ({producto_id: i.id, cantidad: i.cantidad})),
            metodo_pago: metodoPago,
            cliente_id: metodoPago === 'FIADO' ? clienteId : null,
        };

        fetch('/api/vender/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
        })
            .then(r => r.json())
            .then(mostrarComprobante);
    }

    function mostrarComprobante(data) {
        comprobanteInfo.innerHTML = `${data.numero}<br>${data.fecha}<br>${data.usuario_nombre}`;
        comprobanteItems.innerHTML = data.items.map(i => `
            <div class="comprobante-item">
                <div class="comprobante-item-fila">
                    <span>${i.nombre}</span>
                    <span class="plata">${formatearPesos(parseFloat(i.subtotal))}</span>
                </div>
                <div class="comprobante-item-detalle">${i.cantidad} x ${formatearPesos(parseFloat(i.precio_unitario))}</div>
            </div>
        `).join('');
        comprobanteTotal.textContent = formatearPesos(parseFloat(data.total));
        comprobanteMetodo.textContent = data.metodo_pago;
        if (data.saldo_nuevo !== null && data.saldo_nuevo !== undefined) {
            comprobanteSaldo.textContent = `Nuevo saldo de ${data.cliente_nombre}: ${formatearPesos(parseFloat(data.saldo_nuevo))}`;
            comprobanteSaldo.classList.remove('oculto');
        } else {
            comprobanteSaldo.classList.add('oculto');
        }
        overlayComprobante.classList.remove('oculto');
        botonNuevaVenta.focus();
    }

    function cerrarComprobante() {
        overlayComprobante.classList.add('oculto');
        items = [];
        metodoPago = null;
        clienteId = null;
        botonesMetodo.forEach(btn => btn.classList.remove('elegido'));
        bloqueCliente.classList.add('oculto');
        renderTabla();
        buscador.value = '';
        buscador.focus();
    }

    buscador.addEventListener('input', () => {
        clearTimeout(temporizadorBusqueda);
        const q = buscador.value.trim();
        if (!q) {
            ocultarResultados();
            return;
        }
        temporizadorBusqueda = setTimeout(() => buscar(q), 150);
    });

    buscador.addEventListener('keydown', (e) => {
        if (resultadosDiv.classList.contains('oculto')) {
            if (e.key === 'Enter' && buscador.value.trim()) {
                e.preventDefault();
                clearTimeout(temporizadorBusqueda);
                buscar(buscador.value.trim());
            }
            return;
        }
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            indiceSeleccionado = Math.min(indiceSeleccionado + 1, resultadosActuales.length - 1);
            resaltarSeleccion();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            indiceSeleccionado = Math.max(indiceSeleccionado - 1, 0);
            resaltarSeleccion();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (indiceSeleccionado >= 0) {
                agregarProducto(resultadosActuales[indiceSeleccionado]);
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            ocultarResultados();
        }
    });

    resultadosDiv.addEventListener('click', (e) => {
        const fila = e.target.closest('.resultado-item');
        if (fila) {
            agregarProducto(resultadosActuales[parseInt(fila.dataset.indice, 10)]);
        }
    });

    cuerpoVenta.addEventListener('click', (e) => {
        if (e.target.classList.contains('quitar-fila')) {
            const id = parseInt(e.target.dataset.id, 10);
            items = items.filter(i => i.id !== id);
            renderTabla();
            buscador.focus();
        }
    });

    cuerpoVenta.addEventListener('input', (e) => {
        if (!e.target.classList.contains('input-cantidad')) return;
        const id = parseInt(e.target.dataset.id, 10);
        const item = items.find(i => i.id === id);
        if (!item) return;
        const valor = parseFloat(e.target.value);
        item.cantidad = isNaN(valor) ? '' : valor;
        const fila = e.target.closest('tr');
        fila.children[3].textContent = formatearPesos((parseFloat(item.cantidad) || 0) * item.precio_unitario);
        calcularTotales();
    });

    cuerpoVenta.addEventListener('change', (e) => {
        if (!e.target.classList.contains('input-cantidad')) return;
        const id = parseInt(e.target.dataset.id, 10);
        const item = items.find(i => i.id === id);
        if (item && (!item.cantidad || item.cantidad <= 0)) {
            items = items.filter(i => i.id !== id);
            renderTabla();
        }
    });

    cuerpoVenta.addEventListener('keydown', (e) => {
        if (e.target.classList.contains('input-cantidad') && e.key === 'Enter') {
            e.preventDefault();
            buscador.focus();
        }
    });

    botonesMetodo.forEach(btn => btn.addEventListener('click', () => elegirMetodo(btn.dataset.metodo)));
    selectCliente.addEventListener('change', () => {
        clienteId = selectCliente.value || null;
        actualizarSaldoActual();
    });
    window.alClientearCreado = function (cliente) {
        elegirMetodo('FIADO');
        cargarClientes().then(() => {
            selectCliente.value = cliente.id;
            clienteId = String(cliente.id);
            actualizarSaldoActual();
        });
    };

    botonCobrar.addEventListener('click', cobrar);
    botonNuevaVenta.addEventListener('click', cerrarComprobante);

    document.addEventListener('keydown', (e) => {
        const modalAbierto = !overlayComprobante.classList.contains('oculto');

        if (modalAbierto) {
            if (e.key === 'Enter') {
                e.preventDefault();
                cerrarComprobante();
            }
            return;
        }

        if (e.key === 'F2') {
            e.preventDefault();
            if (items.length > 0) {
                if (metodoPago) {
                    cobrar();
                } else {
                    botonesMetodo[0].focus();
                }
            }
            return;
        }

        const activo = document.activeElement;
        const enBuscadorVacio = activo === buscador && buscador.value === '';
        const enCampoTexto = activo && ['INPUT', 'SELECT', 'TEXTAREA'].includes(activo.tagName) && !enBuscadorVacio;

        if (!enCampoTexto && ['1', '2', '3', '4'].includes(e.key)) {
            e.preventDefault();
            const mapa = {'1': 'EFECTIVO', '2': 'NEQUI', '3': 'DAVIPLATA', '4': 'FIADO'};
            elegirMetodo(mapa[e.key]);
            return;
        }

        if (e.key === 'Escape' && resultadosDiv.classList.contains('oculto')) {
            elegirMetodo(null);
        }
    });

    renderTabla();
    buscador.focus();
})();
