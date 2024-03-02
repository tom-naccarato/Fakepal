from django.apps import AppConfig
from django.db.models.signals import post_migrate
from register import create_admin_account


class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'

    # Signal to create the admin group and account after the migration
    def ready(self):
        post_migrate.connect(create_admin_account.create_admin_group_and_account, sender=self)
