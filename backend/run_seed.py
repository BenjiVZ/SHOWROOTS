import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()
exec(open(os.path.join(os.path.dirname(__file__), 'seed_demo.py'), encoding='utf-8').read())
