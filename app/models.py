from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Norma(TimeStampedModel):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.codigo} – {self.nombre}"

class Proceso(TimeStampedModel):
    nombre = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.nombre

class Empleado(TimeStampedModel):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(blank=True)
    def __str__(self):
        return self.nombre

class Capacitacion(TimeStampedModel):
    MODALIDADES = (("Presencial","Presencial"),("Virtual","Virtual"),("Mixta","Mixta"))
    tema = models.CharField(max_length=200)
    programa = models.CharField(max_length=200, blank=True)
    modalidad = models.CharField(max_length=20, choices=MODALIDADES)
    normas = models.ManyToManyField(Norma, blank=True, related_name='capacitaciones')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    responsable = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, related_name='capacitaciones_responsable')
    participantes_estimados = models.PositiveIntegerField(default=1)
    evidencia = models.FileField(upload_to='capacitaciones/', blank=True)
    notas = models.TextField(blank=True)
    def __str__(self):
        return f"{self.tema} ({self.fecha_inicio:%Y-%m-%d})"

class Auditoria(TimeStampedModel):
    normas_a_auditar = models.ManyToManyField(Norma, related_name='auditorias')
    proceso = models.ForeignKey(Proceso, on_delete=models.SET_NULL, null=True, blank=True)
    proceso_texto = models.CharField(max_length=200, blank=True, help_text="Nombre del proceso si no existe en catálogo")
    auditor_lider = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, related_name='auditorias_lider')
    equipo = models.TextField(blank=True, help_text="Nombres separados por coma")
    es_proveedor = models.BooleanField(default=False)
    fecha = models.DateField(default=timezone.now)
    anexos = models.FileField(upload_to='auditorias/', blank=True)
    alcance = models.TextField(blank=True)
    def __str__(self):
        base = self.proceso.nombre if self.proceso else self.proceso_texto or 'Sin proceso'
        return f"Auditoría {base} – {self.fecha:%Y-%m-%d}"

class Expediente(TimeStampedModel):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='expedientes')
    curp = models.CharField(max_length=18, blank=True)
    nss = models.CharField(max_length=15, blank=True)
    fecha_ingreso = models.DateField()
    paquete_documentos = models.FileField(upload_to='expedientes/', blank=True)
    notas = models.TextField(blank=True)
    def __str__(self):
        return f"Expediente de {self.empleado}"

class MetodologiaDigitalizacion(TimeStampedModel):
    TIPOS = (("Contrato","Contrato"),("Expediente","Expediente"),("Otro","Otro"))
    tipo_documento = models.CharField(max_length=30, choices=TIPOS)
    resolucion_dpi = models.PositiveIntegerField(default=300)
    responsable = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    fecha_meta = models.DateField()
    lineamientos = models.TextField(blank=True)
    def __str__(self):
        return f"Metodología {self.tipo_documento} ({self.resolucion_dpi} DPI)"

class HomologacionSGC(TimeStampedModel):
    normas_involucradas = models.ManyToManyField(Norma, related_name='homologaciones')
    proceso = models.ForeignKey(Proceso, on_delete=models.SET_NULL, null=True, blank=True)
    documento_equivalente = models.CharField(max_length=200)
    propuesta = models.TextField()
    responsable = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    adjunto = models.FileField(upload_to='homologacion/', blank=True)
    def __str__(self):
        return f"Homologación – {self.documento_equivalente}"

class DocumentoSGC(TimeStampedModel):
    ESTADOS = (("Borrador","Borrador"),("En revisión","En revisión"),("Aprobado","Aprobado"),("Obsoleto","Obsoleto"))
    TIPOS = (("Procedimiento","Procedimiento"),("Instructivo","Instructivo"),("Formato","Formato"),("Política","Política"))
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=30, choices=TIPOS)
    codigo = models.CharField(max_length=50)
    version = models.CharField(max_length=10, default="1.0")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Borrador")
    propietario = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, related_name='documentos_propietario')
    revisores = models.ManyToManyField(Empleado, blank=True, related_name='documentos_a_revisar')
    archivo = models.FileField(upload_to='documentos/', blank=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    comentarios = models.TextField(blank=True)
    class Meta:
        unique_together = ('codigo', 'version')
    def __str__(self):
        return f"{self.codigo} v{self.version} – {self.titulo}"