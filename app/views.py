from django.shortcuts import render, redirect
from django.contrib import messages
from .models import (
    Norma, Proceso, Empleado,
    Capacitacion, Auditoria, Expediente,
    MetodologiaDigitalizacion, HomologacionSGC, DocumentoSGC,
)
from django.core.paginator import Paginator
from django.db.models import Q

SECCIONES = {
    'calidad_rh': {
        'titulo': 'Calidad / RH – Gestión de capacitaciones',
        'justificacion': 'Optimizar gestión de CAI/CDMI para liberar tiempo en RH y Calidad.',
        'propuestas': ['Uso de plataforma centralizada', 'Prototipo de software']
    },
    'calidad': {
        'titulo': 'Calidad – Auditorías internas y a proveedores',
        'justificacion': 'Optimizar tiempos de operación administrativa.',
        'propuestas': ['Checklist inteligente y auditoría de dos normas a la vez']
    },
    'rh': {
        'titulo': 'RH – Gestión de expedientes',
        'justificacion': 'Optimizar tiempos administrativos.',
        'propuestas': ['Expediente electrónico', 'Metodología de digitalización']
    },
    'dos_sgc': {
        'titulo': 'Dos SGC – Homologación',
        'justificacion': 'Mismas actividades con requisitos distintos en 2 SGC.',
        'propuestas': ['Matriz de equivalencias y homologación de 4 normas']
    },
    'sgc': {
        'titulo': 'SGC – Gestión documental',
        'justificacion': 'Centralizar actualización/revisión/aprobación de documentos.',
        'propuestas': ['Plataforma de gestión documental']
    },
}

def menu_principal(request):
    return render(request, 'menu.html', {'secciones': SECCIONES})

def _paginate(request, qs, per_page=25):
    return Paginator(qs, per_page).get_page(request.GET.get('page'))

# CAPACITACIONES

def calidad_rh(request):
    if request.method == 'POST':
        try:
            responsable = Empleado.objects.filter(id=request.POST.get('responsable')).first()
            obj = Capacitacion.objects.create(
                tema=request.POST.get('tema'),
                programa=request.POST.get('programa',''),
                modalidad=request.POST.get('modalidad'),
                fecha_inicio=request.POST.get('fecha_inicio'),
                fecha_fin=request.POST.get('fecha_fin'),
                responsable=responsable,
                participantes_estimados=int(request.POST.get('participantes_estimados') or 1),
                evidencia=request.FILES.get('evidencia'),
                notas=request.POST.get('notas','')
            )
            obj.normas.set(Norma.objects.filter(id__in=request.POST.getlist('normas')))
            messages.success(request, 'Capacitación guardada.')
            return redirect('calidad_rh')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    ctx = {'meta': SECCIONES['calidad_rh'], 'normas': Norma.objects.all(), 'empleados': Empleado.objects.all()}
    return render(request, 'calidad_rh.html', ctx)


def hist_capacitaciones(request):
    qs = (Capacitacion.objects
          .select_related('responsable')
          .prefetch_related('normas')
          .order_by('-created_at'))
    q = request.GET.get('q', '').strip()
    modalidad = request.GET.get('modalidad')
    norma = request.GET.get('norma')
    if q:
        qs = qs.filter(
            Q(tema__icontains=q) | Q(programa__icontains=q) |
            Q(notas__icontains=q) | Q(responsable__nombre__icontains=q)
        )
    if modalidad:
        qs = qs.filter(modalidad=modalidad)
    if norma:
        qs = qs.filter(normas__id=norma)
    page = _paginate(request, qs)
    return render(request, 'hist_capacitaciones.html', {'page': page})


# AUDITORÍAS

def calidad(request):
    if request.method == 'POST':
        try:
            auditor_lider = Empleado.objects.filter(id=request.POST.get('auditor_lider')).first()
            proceso = Proceso.objects.filter(id=request.POST.get('proceso')).first() if request.POST.get('proceso') else None
            obj = Auditoria.objects.create(
                proceso=proceso,
                proceso_texto=request.POST.get('proceso_texto',''),
                auditor_lider=auditor_lider,
                equipo=request.POST.get('equipo',''),
                es_proveedor=bool(request.POST.get('es_proveedor')),
                fecha=request.POST.get('fecha'),
                anexos=request.FILES.get('anexos'),
                alcance=request.POST.get('alcance',''),
            )
            obj.normas_a_auditar.set(Norma.objects.filter(id__in=request.POST.getlist('normas_a_auditar')))
            messages.success(request, 'Auditoría registrada.')
            return redirect('calidad')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    ctx = {'meta': SECCIONES['calidad'], 'normas': Norma.objects.all(), 'procesos': Proceso.objects.all(), 'empleados': Empleado.objects.all()}
    return render(request, 'calidad.html', ctx)


def hist_auditorias(request):
    qs = (Auditoria.objects
          .select_related('proceso', 'auditor_lider')
          .prefetch_related('normas_a_auditar')
          .order_by('-fecha', '-created_at'))
    q = request.GET.get('q', '').strip()
    norma = request.GET.get('norma')
    proveedor = request.GET.get('proveedor')  # '1' o '0'
    if q:
        qs = qs.filter(
            Q(proceso__nombre__icontains=q) |
            Q(proceso_texto__icontains=q) |
            Q(auditor_lider__nombre__icontains=q) |
            Q(equipo__icontains=q)
        )
    if norma:
        qs = qs.filter(normas_a_auditar__id=norma)
    if proveedor in ('0', '1'):
        qs = qs.filter(es_proveedor=(proveedor == '1'))
    page = _paginate(request, qs)
    return render(request, 'hist_auditorias.html', {'page': page})

# RH

def rh(request):
    if request.method == 'POST':
        if 'exp-submit' in request.POST:
            try:
                empleado = Empleado.objects.filter(id=request.POST.get('empleado')).first()
                Expediente.objects.create(
                    empleado=empleado,
                    curp=request.POST.get('curp',''),
                    nss=request.POST.get('nss',''),
                    fecha_ingreso=request.POST.get('fecha_ingreso'),
                    paquete_documentos=request.FILES.get('paquete_documentos'),
                    notas=request.POST.get('notas','')
                )
                messages.success(request, 'Expediente guardado.')
                return redirect('rh')
            except Exception as e:
                messages.error(request, f'Error expediente: {e}')
        elif 'dig-submit' in request.POST:
            try:
                responsable = Empleado.objects.filter(id=request.POST.get('responsable')).first()
                MetodologiaDigitalizacion.objects.create(
                    tipo_documento=request.POST.get('tipo_documento'),
                    resolucion_dpi=int(request.POST.get('resolucion_dpi') or 300),
                    responsable=responsable,
                    fecha_meta=request.POST.get('fecha_meta'),
                    lineamientos=request.POST.get('lineamientos','')
                )
                messages.success(request, 'Metodología guardada.')
                return redirect('rh')
            except Exception as e:
                messages.error(request, f'Error metodología: {e}')
    ctx = {'meta': SECCIONES['rh'], 'empleados': Empleado.objects.all()}
    return render(request, 'rh.html', ctx)

def hist_expedientes(request):
    qs = Expediente.objects.select_related('empleado').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(empleado__nombre__icontains=q) |
            Q(curp__icontains=q) |
            Q(nss__icontains=q) |
            Q(notas__icontains=q)
        )
    page = _paginate(request, qs)
    return render(request, 'hist_expedientes.html', {'page': page})

def hist_metodologias(request):
    qs = MetodologiaDigitalizacion.objects.select_related('responsable').order_by('-created_at')
    tipo = request.GET.get('tipo')
    if tipo:
        qs = qs.filter(tipo_documento=tipo)
    page = _paginate(request, qs)
    return render(request, 'hist_metodologias.html', {'page': page})

def hist_homologaciones(request):
    qs = (HomologacionSGC.objects
          .select_related('proceso', 'responsable')
          .prefetch_related('normas_involucradas')
          .order_by('-created_at'))
    norma = request.GET.get('norma')
    if norma:
        qs = qs.filter(normas_involucradas__id=norma)
    page = _paginate(request, qs)
    return render(request, 'hist_homologaciones.html', {'page': page})


# DOS SGC

def dos_sgc(request):
    if request.method == 'POST':
        try:
            proceso = Proceso.objects.filter(id=request.POST.get('proceso')).first() if request.POST.get('proceso') else None
            responsable = Empleado.objects.filter(id=request.POST.get('responsable')).first()
            obj = HomologacionSGC.objects.create(
                proceso=proceso,
                documento_equivalente=request.POST.get('documento_equivalente'),
                propuesta=request.POST.get('propuesta'),
                responsable=responsable,
                adjunto=request.FILES.get('adjunto')
            )
            obj.normas_involucradas.set(Norma.objects.filter(id__in=request.POST.getlist('normas_involucradas')))
            messages.success(request, 'Propuesta de homologación guardada.')
            return redirect('dos_sgc')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    ctx = {'meta': SECCIONES['dos_sgc'], 'normas': Norma.objects.all(), 'procesos': Proceso.objects.all(), 'empleados': Empleado.objects.all()}
    return render(request, 'dos_sgc.html', ctx)

def hist_documentos(request):
    qs = DocumentoSGC.objects.select_related('propietario').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado')
    tipo = request.GET.get('tipo')
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(codigo__icontains=q) | Q(comentarios__icontains=q))
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    page = _paginate(request, qs)
    return render(request, 'hist_documentos.html', {'page': page})

# SGC

def sgc(request):
    if request.method == 'POST':
        try:
            propietario = Empleado.objects.filter(id=request.POST.get('propietario')).first()
            obj = DocumentoSGC.objects.create(
                titulo=request.POST.get('titulo'),
                tipo=request.POST.get('tipo'),
                codigo=request.POST.get('codigo'),
                version=request.POST.get('version') or '1.0',
                estado=request.POST.get('estado'),
                propietario=propietario,
                archivo=request.FILES.get('archivo'),
                fecha_emision=request.POST.get('fecha_emision'),
                fecha_vencimiento=request.POST.get('fecha_vencimiento') or None,
                comentarios=request.POST.get('comentarios','')
            )
            revisores_ids = request.POST.getlist('revisores')
            if revisores_ids:
                obj.revisores.set(Empleado.objects.filter(id__in=revisores_ids))
            messages.success(request, 'Documento guardado.')
            return redirect('sgc')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    ctx = {'meta': SECCIONES['sgc'], 'empleados': Empleado.objects.all(), 'estados': DocumentoSGC.ESTADOS, 'tipos': DocumentoSGC.TIPOS}
    return render(request, 'sgc.html', ctx)