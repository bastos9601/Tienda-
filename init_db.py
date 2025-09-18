#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db

def init_database():
    """Inicializar la base de datos creando todas las tablas"""
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada correctamente")
        print("📊 Tablas creadas:")
        for table in db.metadata.tables:
            print(f"   - {table}")

if __name__ == "__main__":
    init_database()
