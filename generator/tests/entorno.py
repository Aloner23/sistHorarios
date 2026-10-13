"""Plugin de pytest (cargado con ``-p``) que fija un entorno de desarrollo
antes de que pytest-django importe la configuración."""

import os

os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("SECRET_KEY", "clave-solo-para-pruebas")
