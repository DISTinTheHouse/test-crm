from django.urls import path

from proyecto import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.menu_principal, name='menu'),
    # Secciones
    path('calidad-rh/', views.calidad_rh, name='calidad_rh'),
    path('calidad-rh/historial/', views.hist_capacitaciones, name='hist_capacitaciones'),

    path('calidad/', views.calidad, name='calidad'),
    path('calidad/historial/', views.hist_auditorias, name='hist_auditorias'),

    path('rh/', views.rh, name='rh'),
    path('rh/expedientes/', views.hist_expedientes, name='hist_expedientes'),
    path('rh/metodologias/', views.hist_metodologias, name='hist_metodologias'),

    path('dos-sgc/', views.dos_sgc, name='dos_sgc'),
    path('dos-sgc/historial/', views.hist_homologaciones, name='hist_homologaciones'),

    path('sgc/', views.sgc, name='sgc'),
    path('sgc/historial/', views.hist_documentos, name='hist_documentos')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)