#!/usr/bin/env python3
"""
Script para inicializar la base de datos en Koyeb
Este script se ejecuta automáticamente cuando se despliega la aplicación
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configurar Flask para la inicialización
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')

# Configuración de base de datos
database_url = os.environ.get('DATABASE_URL')
if database_url and ('postgresql' in database_url or 'postgres' in database_url):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'sslmode': 'require'}
    }
else:
    print("Error: DATABASE_URL no está configurada o no es PostgreSQL")
    sys.exit(1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Importar modelos desde app.py
with app.app_context():
    # Importar todos los modelos
    from app import Categoria, Producto, Pedido, Usuario
    
    def init_database():
        """Inicializar la base de datos con datos básicos"""
        try:
            print("Creando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente")
            
            # Verificar si ya existen categorías
            if Categoria.query.count() == 0:
                print("Creando categorías por defecto...")
                
                categorias_default = [
                    {
                        'nombre': 'Bebidas',
                        'descripcion': 'Refrescos, jugos y bebidas frías',
                        'icono': 'fas fa-coffee',
                        'color': '#28a745'
                    },
                    {
                        'nombre': 'Snacks',
                        'descripcion': 'Papas, galletas y aperitivos',
                        'icono': 'fas fa-cookie-bite',
                        'color': '#ffc107'
                    },
                    {
                        'nombre': 'Dulces',
                        'descripcion': 'Caramelos, chocolates y golosinas',
                        'icono': 'fas fa-candy-cane',
                        'color': '#dc3545'
                    },
                    {
                        'nombre': 'Lácteos',
                        'descripcion': 'Leche, yogurt y productos lácteos',
                        'icono': 'fas fa-glass-whiskey',
                        'color': '#17a2b8'
                    }
                ]
                
                for cat_data in categorias_default:
                    categoria = Categoria(**cat_data)
                    db.session.add(categoria)
                
                db.session.commit()
                print("Categorías creadas exitosamente")
            else:
                print("Las categorías ya existen")
            
            # Verificar si ya existe un usuario admin
            if Usuario.query.filter_by(username='admin').first() is None:
                print("Creando usuario administrador...")
                from werkzeug.security import generate_password_hash
                
                admin_user = Usuario(
                    username='admin',
                    email='admin@tienda.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Usuario administrador creado (usuario: admin, contraseña: admin123)")
            else:
                print("El usuario administrador ya existe")
            
            print("Base de datos inicializada correctamente")
            return True
            
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            db.session.rollback()
            return False
    
    if __name__ == '__main__':
        print("Inicializando base de datos para Koyeb...")
        success = init_database()
        if success:
            print("✅ Base de datos inicializada exitosamente")
            sys.exit(0)
        else:
            print("❌ Error al inicializar la base de datos")
            sys.exit(1)
