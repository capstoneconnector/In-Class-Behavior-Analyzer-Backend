from django.apps import AppConfig
import os, subprocess


class ApiConfig(AppConfig):
    name = 'api'
    app_name = 'api'

    def ready(self):
        manage_path = os.getcwd() + '\\manage.py'
        print(manage_path)
        subprocess.run('python ' + manage_path + ' runworkers')
        subprocess.call(['python', 'manage.py', 'migrate'])
        print('Started workers!')
