from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = 'Uživatelé'

    def ready(self):
        import users.signals