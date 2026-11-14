import os
import sys

def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbas_portal.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])

if __name__ == '__main__':
    run()
