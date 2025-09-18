#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación Flask
from app import app as application

if __name__ == "__main__":
    application.run()
