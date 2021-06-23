from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'catalog'
    verbose_name = 'Katalog'

    def ready(self):
        import catalog.signals