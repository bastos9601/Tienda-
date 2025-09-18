#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para inicializar la base de datos en Render
Ejecutar después del despliegue para crear tablas y datos iniciales
"""

import os
from app import app, db, Usuario, Categoria, Producto
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa la base de datos con datos por defecto"""
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas de la base de datos creadas")
        
        # Crear usuario administrador si no existe
        if Usuario.query.count() == 0:
            admin = Usuario(
                username='admin',
                email='admin@tienda.com',
                es_admin=True
            )
            admin.set_password('admin123')  # Cambia esta contraseña en producción
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   ⚠️  CAMBIA ESTA CONTRASEÑA EN PRODUCCIÓN")
        
        # Crear categorías de ejemplo si no existen
        if Categoria.query.count() == 0:
            categorias_ejemplo = [
                Categoria(nombre="Comida Rápida", descripcion="Hamburguesas, pizzas y comida rápida", icono="fas fa-hamburger", color="#ff6b35"),
                Categoria(nombre="Bebidas", descripcion="Refrescos, jugos y bebidas", icono="fas fa-coffee", color="#4ecdc4"),
                Categoria(nombre="Postres", descripcion="Helados, pasteles y dulces", icono="fas fa-ice-cream", color="#ffe66d"),
                Categoria(nombre="Saludable", descripcion="Ensaladas y opciones saludables", icono="fas fa-leaf", color="#95e1d3"),
            ]
            
            for categoria in categorias_ejemplo:
                db.session.add(categoria)
            
            db.session.commit()
            print("✅ Categorías de ejemplo creadas")
        
        # Crear productos de ejemplo si no existen
        if Producto.query.count() == 0:
            # Obtener las categorías creadas
            categoria_comida = Categoria.query.filter_by(nombre="Comida Rápida").first()
            categoria_bebidas = Categoria.query.filter_by(nombre="Bebidas").first()
            categoria_postres = Categoria.query.filter_by(nombre="Postres").first()
            categoria_saludable = Categoria.query.filter_by(nombre="Saludable").first()
            
            productos_ejemplo = [
                Producto(nombre="Pizza Margherita", descripcion="Pizza clásica con tomate, mozzarella y albahaca", precio=12.99, stock=10, categoria_id=categoria_comida.id if categoria_comida else None),
                Producto(nombre="Hamburguesa Clásica", descripcion="Hamburguesa con carne, lechuga, tomate y queso", precio=8.99, stock=15, categoria_id=categoria_comida.id if categoria_comida else None),
                Producto(nombre="Ensalada César", descripcion="Ensalada fresca con pollo, lechuga y aderezo césar", precio=6.99, stock=8, categoria_id=categoria_saludable.id if categoria_saludable else None),
                Producto(nombre="Pasta Carbonara", descripcion="Pasta con salsa carbonara y panceta", precio=10.99, stock=12, categoria_id=categoria_comida.id if categoria_comida else None),
                Producto(nombre="Coca Cola", descripcion="Refresco de cola 500ml", precio=2.50, stock=20, categoria_id=categoria_bebidas.id if categoria_bebidas else None),
                Producto(nombre="Helado de Vainilla", descripcion="Helado cremoso de vainilla", precio=4.99, stock=10, categoria_id=categoria_postres.id if categoria_postres else None),
            ]
            
            for producto in productos_ejemplo:
                db.session.add(producto)
            
            db.session.commit()
            print("✅ Productos de ejemplo creados")
        
        print("🎉 Base de datos inicializada correctamente")

if __name__ == '__main__':
    init_database()
