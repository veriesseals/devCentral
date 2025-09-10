from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social'
    # label = 'devcentral_social'

    def ready(self):
        from . import signals # Import signals to ensure they are registered