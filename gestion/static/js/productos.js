(function () {
    const overlay = document.getElementById('overlay-producto');
    const tituloModal = document.getElementById('modal-titulo-producto');
    const zonaEliminar = document.getElementById('zona-eliminar');
    const errorProducto = document.getElementById('error-producto');
    const margen = document.getElementById('margen-calculado');

    const campos = ['codigo_interno', 'codigo_barras', 'nombre', 'marca', 'categoria_id',
        'tipo_venta', 'precio_compra', 'precio_venta', 'stock', 'stock_minimo',
        'proveedor_id', 'fecha_vencimiento'];

    let idActual = null;

    function elemento(nombre) {
        return document.getElementById('f-' + nombre);
    }

    function formatearPesos(valor) {
        return '$' + Math.round(valor || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function numero(nombre) {
        const limpio = elemento(nombre).value.replace(/[^\d.]/g, '');
        return limpio ? parseFloat(limpio) : 0;
    }

    function recalcularMargen() {
        const compra = numero('precio_compra');
        const venta = numero('precio_venta');
        if (compra > 0 && venta > 0) {
            const ganancia = venta - compra;
            const porcentaje = Math.round(ganancia / compra * 100);
            margen.textContent = 'Ganancia por unidad: ' + formatearPesos(ganancia) + ' (' + porcentaje + '%)';
            margen.classList.toggle('margen-negativo', ganancia <= 0);
        } else {
            margen.textContent = '';
        }
    }

    function abrir(fila) {
        errorProducto.classList.add('oculto');
        if (fila) {
            idActual = fila.dataset.id;
            tituloModal.textContent = 'Editar producto';
            zonaEliminar.classList.remove('oculto');
            campos.forEach(nombre => { elemento(nombre).value = fila.dataset[nombre] || ''; });
        } else {
            idActual = null;
            tituloModal.textContent = 'Nuevo producto';
            zonaEliminar.classList.add('oculto');
            campos.forEach(nombre => { elemento(nombre).value = ''; });
            elemento('tipo_venta').value = 'UNIDAD';
            elemento('categoria_id').selectedIndex = 0;
            elemento('stock').value = '0';
            elemento('stock_minimo').value = '5';
        }
        recalcularMargen();
        overlay.classList.remove('oculto');
        elemento('nombre').focus();
    }

    function cerrar() {
        overlay.classList.add('oculto');
    }

    function guardar() {
        if (!elemento('nombre').value.trim() || !elemento('codigo_interno').value.trim()) {
            errorProducto.textContent = 'El nombre y el código interno son obligatorios';
            errorProducto.classList.remove('oculto');
            return;
        }
        const datos = {
            id: idActual,
            nombre: elemento('nombre').value.trim(),
            marca: elemento('marca').value.trim(),
            codigo_interno: elemento('codigo_interno').value.trim(),
            codigo_barras: elemento('codigo_barras').value.trim(),
            categoria_id: elemento('categoria_id').value,
            tipo_venta: elemento('tipo_venta').value,
            precio_compra: numero('precio_compra'),
            precio_venta: numero('precio_venta'),
            stock: numero('stock'),
            stock_minimo: numero('stock_minimo'),
            proveedor_id: elemento('proveedor_id').value,
            fecha_vencimiento: elemento('fecha_vencimiento').value,
        };
        fetch('/api/producto/guardar/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(datos),
        })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    errorProducto.textContent = data.error;
                    errorProducto.classList.remove('oculto');
                    return;
                }
                location.reload();
            });
    }

    function eliminar() {
        if (!confirm('¿Quitar este producto del catálogo?')) return;
        fetch('/api/producto/eliminar/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: idActual}),
        }).then(() => location.reload());
    }

    document.getElementById('boton-nuevo').addEventListener('click', () => abrir(null));
    document.getElementById('producto-cancelar').addEventListener('click', cerrar);
    document.getElementById('producto-guardar').addEventListener('click', guardar);
    document.getElementById('producto-eliminar').addEventListener('click', eliminar);
    elemento('precio_compra').addEventListener('input', recalcularMargen);
    elemento('precio_venta').addEventListener('input', recalcularMargen);

    document.querySelectorAll('.fila-producto').forEach(fila => {
        fila.addEventListener('click', () => abrir(fila));
    });

    document.addEventListener('keydown', (e) => {
        if (overlay.classList.contains('oculto')) return;
        if (e.key === 'Escape') {
            e.preventDefault();
            cerrar();
        }
    });
})();
