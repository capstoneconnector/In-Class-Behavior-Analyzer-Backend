from django.apps import AppConfig
import os, subprocess


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        manage_path = os.getcwd() + '\\manage.py'
        subprocess.run('python ' + manage_path + ' runworkers')
        print('Started workers!')
