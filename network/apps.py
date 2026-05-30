from django.apps import AppConfig

class NetworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'network'

    def ready(self):
        # This imports your signals so they are registered when Django starts
        import network.signals