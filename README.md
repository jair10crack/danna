# Demo Hipermercado Danna

Demostración de sistema de gestión para supermercado. **No es software de producción:**
los datos son de ejemplo y se borran con el botón "Reiniciar demostración".

## Correr en tu computador

Necesitás Python 3.11 o superior.

```bash
git clone <URL-DEL-REPO>
cd danna

python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Abrí http://127.0.0.1:8000

## Códigos de acceso

| Código | Usuario | Rol |
|---|---|---|
| 1234 | Carlos Danna | Administrador |
| 5678 | Yesenia Rojas | Cajero |

## Pantallas

- **Venta** — buscar o escanear, Enter para agregar, teclas 1-4 para el método de pago, F2 para cobrar
- **Fiados** — saldos por cliente, estado de cuenta y registro de abonos
- **Dashboard** — indicadores del día y ventas de los últimos 7 días
- **Productos** — catálogo completo, crear y editar
- **Inventario** — agotados y bajo mínimo

## Recargar los datos de ejemplo

```bash
python manage.py cargar_demo
```
