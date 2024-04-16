from threading import Thread

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from register import create_admin_account
from thrift_timestamp import server


class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'

    def ready(self):
        # Start the Thrift server in a separate thread
        thrift_server_thread = Thread(target=thrift_server.start_thrift_server)
        thrift_server_thread.daemon = True
        thrift_server_thread.start()

        # Connect the post_migrate signal
        post_migrate.connect(create_admin_account.create_admin_group_and_account, sender=self)

