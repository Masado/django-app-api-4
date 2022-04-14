"""gunicorn WSGI server configuration"""
from multiprocessing import cpu_count
from os import environ

timeout = 18000
workers = cpu_count() * 2 + 1
