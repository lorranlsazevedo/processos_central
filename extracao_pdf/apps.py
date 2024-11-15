from django.apps import AppConfig

class ExtracaoPdfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'extracao_pdf'
    verbose_name = 'Central de Processos'

    def ready(self):
        import extracao_pdf.signals
