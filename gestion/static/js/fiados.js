(function () {
    const overlay = document.getElementById('overlay-abono');
    const botonAbonar = document.getElementById('boton-abonar');
    const botonCancelar = document.getElementById('abono-cancelar');
    const botonConfirmar = document.getElementById('abono-confirmar');
    const saldoCliente = document.getElementById('saldo-cliente');
    const abonoSaldo = document.getElementById('abono-saldo');
    const abonoValor = document.getElementById('abono-valor');
    const abonoEfectivo = document.getElementById('abono-efectivo');
    const abonoVueltas = document.getElementById('abono-vueltas');
    const abonoError = document.getElementById('abono-error');

    let saldo = parseFloat(saldoCliente.dataset.saldo);

    function formatearPesos(valor) {
        const entero = Math.round(valor || 0);
        return '$' + entero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function numero(input) {
        const limpio = input.value.replace(/[^\d]/g, '');
        return limpio ? parseInt(limpio, 10) : 0;
    }

    function mostrarError(texto) {
        abonoError.textContent = texto;
        abonoError.classList.remove('oculto');
    }

    function limpiarError() {
        abonoError.classList.add('oculto');
    }

    function recalcular() {
        const valor = numero(abonoValor);
        const efectivo = numero(abonoEfectivo);
        abonoVueltas.textContent = formatearPesos(Math.max(efectivo - valor, 0));
        if (valor > saldo) {
            mostrarError('El abono no puede ser mayor al saldo');
        } else if (efectivo && efectivo < valor) {
            mostrarError('El efectivo recibido es menor al abono');
        } else {
            limpiarError();
        }
    }

    function abrir() {
        abonoSaldo.textContent = formatearPesos(saldo);
        abonoValor.value = Math.round(saldo).toString();
        abonoEfectivo.value = '';
        abonoVueltas.textContent = '$0';
        limpiarError();
        overlay.classList.remove('oculto');
        abonoValor.focus();
        abonoValor.select();
    }

    function cerrar() {
        overlay.classList.add('oculto');
    }

    function confirmar() {
        const valor = numero(abonoValor);
        if (valor <= 0 || valor > saldo) {
            mostrarError('El abono no puede ser mayor al saldo');
            return;
        }
        fetch('/api/abonar/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({cliente_id: window.CLIENTE_ID, valor: valor}),
        })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    mostrarError(data.error);
                    return;
                }
                location.reload();
            });
    }

    botonAbonar.addEventListener('click', abrir);
    botonCancelar.addEventListener('click', cerrar);
    botonConfirmar.addEventListener('click', confirmar);
    abonoValor.addEventListener('input', recalcular);
    abonoEfectivo.addEventListener('input', recalcular);

    document.addEventListener('keydown', (e) => {
        if (overlay.classList.contains('oculto')) return;
        if (e.key === 'Escape') {
            e.preventDefault();
            cerrar();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            confirmar();
        }
    });
})();
