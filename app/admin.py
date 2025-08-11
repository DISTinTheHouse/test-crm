from django.contrib import admin
from .models import (Norma, Proceso, Empleado, Capacitacion, Auditoria, Expediente, MetodologiaDigitalizacion, HomologacionSGC, DocumentoSGC)

@admin.register(Norma)
class NormaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "created_at")
    search_fields = ("codigo", "nombre")

@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    search_fields = ("nombre",)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "correo")
    search_fields = ("nombre", "correo")

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ("tema", "modalidad", "fecha_inicio", "fecha_fin")
    list_filter = ("modalidad", "fecha_inicio")
    search_fields = ("tema", "programa")
    filter_horizontal = ("normas",)

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "es_proveedor", "auditor_lider")
    list_filter = ("es_proveedor", "fecha")
    filter_horizontal = ("normas_a_auditar",)

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha_ingreso")
    search_fields = ("empleado__nombre", "curp", "nss")

@admin.register(MetodologiaDigitalizacion)
class MetodologiaAdmin(admin.ModelAdmin):
    list_display = ("tipo_documento", "resolucion_dpi", "responsable", "fecha_meta")

@admin.register(HomologacionSGC)
class HomologacionAdmin(admin.ModelAdmin):
    list_display = ("documento_equivalente", "responsable")
    filter_horizontal = ("normas_involucradas",)

@admin.register(DocumentoSGC)
class DocumentoSGCAdmin(admin.ModelAdmin):
    list_display = ("codigo", "version", "titulo", "estado", "propietario")
    list_filter = ("estado", "tipo")
    search_fields = ("codigo", "titulo")
    filter_horizontal = ("revisores",)