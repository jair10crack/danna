from django.urls import path
from django.views.generic import RedirectView

from gestion import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='venta')),
    path('login/', views.login_vista, name='login'),
    path('logout/', views.logout_vista, name='logout'),
    path('reiniciar/', views.reiniciar_vista, name='reiniciar'),
    path('venta/', views.venta_vista, name='venta'),
    path('fiados/', views.fiados_vista, name='fiados'),
    path('fiados/<int:cliente_id>/', views.fiado_detalle_vista, name='fiado_detalle'),
    path('dashboard/', views.dashboard_vista, name='dashboard'),
    path('productos/', views.productos_vista, name='productos'),
    path('inventario/', views.inventario_vista, name='inventario'),
    path('api/buscar/', views.buscar_api, name='api_buscar'),
    path('api/vender/', views.vender_api, name='api_vender'),
    path('api/clientes/', views.clientes_api, name='api_clientes'),
    path('api/abonar/', views.abonar_api, name='api_abonar'),
    path('api/producto/guardar/', views.producto_guardar_api, name='api_producto_guardar'),
    path('api/producto/eliminar/', views.producto_eliminar_api, name='api_producto_eliminar'),
    path('api/cliente/guardar/', views.cliente_guardar_api, name='api_cliente_guardar'),
]
