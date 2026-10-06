window.abrirNuevoCliente = (function () {
    const overlay = document.getElementById('overlay-cliente');
    const errorCliente = document.getElementById('error-cliente');
    const campos = ['nombre', 'telefono', 'documento', 'direccion'];

    function elemento(nombre) {
        return document.getElementById('c-' + nombre);
    }

    function abrir() {
        campos.forEach(nombre => { elemento(nombre).value = ''; });
        document.getElementById('c-limite').value = '500000';
        errorCliente.classList.add('oculto');
        overlay.classList.remove('oculto');
        elemento('nombre').focus();
    }

    function cerrar() {
        overlay.classList.add('oculto');
    }

    function guardar() {
        const nombre = elemento('nombre').value.trim();
        if (!nombre) {
            errorCliente.textContent = 'El nombre es obligatorio';
            errorCliente.classList.remove('oculto');
            return;
        }
        fetch('/api/cliente/guardar/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                nombre: nombre,
                telefono: elemento('telefono').value.trim(),
                documento: elemento('documento').value.trim(),
                direccion: elemento('direccion').value.trim(),
                limite_credito: document.getElementById('c-limite').value.replace(/[^\d]/g, '') || 500000,
            }),
        })
            .then(r => r.json())
            .then(data => {
                cerrar();
                if (window.alClientearCreado) {
                    window.alClientearCreado(data);
                } else {
                    location.reload();
                }
            });
    }

    document.getElementById('cliente-cancelar').addEventListener('click', cerrar);
    document.getElementById('cliente-guardar').addEventListener('click', guardar);
    document.getElementById('boton-nuevo-cliente').addEventListener('click', abrir);

    document.addEventListener('keydown', (e) => {
        if (overlay.classList.contains('oculto')) return;
        if (e.key === 'Escape') {
            e.preventDefault();
            cerrar();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            guardar();
        }
    });

    return abrir;
})();
