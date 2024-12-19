from django.apps import AppConfig
from django.core.management import call_command


class LibrarywebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'libraryweb'
    def ready(self):
        import libraryweb.signals
        call_command('update_late_fees')