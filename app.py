from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import json

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu-clave-secreta-aqui')

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuración de base de datos para desarrollo y producción
database_url = os.environ.get('DATABASE_URL')
if database_url and ('postgresql' in database_url or 'postgres' in database_url):
    # Producción (Koyeb con PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    # Configuraciones adicionales para PostgreSQL en producción
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'sslmode': 'require'}
    }
else:
    # Desarrollo (SQLite local)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "tienda.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Modelos de la base de datos
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(50), default='fas fa-tag')  # Icono de Font Awesome
    color = db.Column(db.String(20), default='#007bff')  # Color hexadecimal
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con productos
    productos = db.relationship('Producto', backref='categoria', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'color': self.color,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'total_productos': len(self.productos) if self.productos else 0
        }

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el objeto Producto a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'imagen': self.imagen,
            'stock': self.stock,
            'activo': self.activo,
            'categoria_id': self.categoria_id,
            'categoria_nombre': self.categoria.nombre if self.categoria else 'Sin categoría',
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    cliente_telefono = db.Column(db.String(20), nullable=False)
    cliente_direccion = db.Column(db.Text)
    cliente_comentarios = db.Column(db.Text)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmado, entregado
    fecha_pedido = db.Column(db.DateTime, default=datetime.now)
    items = db.relationship('PedidoItem', backref='pedido', lazy=True)
    
    def to_dict(self):
        """Convierte el objeto Pedido a diccionario para JSON"""
        return {
            'id': self.id,
            'cliente_nombre': self.cliente_nombre,
            'cliente_telefono': self.cliente_telefono,
            'cliente_direccion': self.cliente_direccion,
            'cliente_comentarios': self.cliente_comentarios,
            'total': self.total,
            'estado': self.estado,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'items': [item.to_dict() for item in self.items]
        }

class PedidoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto', backref='pedido_items')
    
    def to_dict(self):
        """Convierte el objeto PedidoItem a diccionario para JSON"""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'producto': self.producto.to_dict() if self.producto else None
        }

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    es_admin = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Establece la contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convierte el objeto Usuario a diccionario para JSON"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'es_admin': self.es_admin,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.String(200))
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_valor(clave, valor_default=''):
        """Obtiene el valor de una configuración"""
        config = Configuracion.query.filter_by(clave=clave).first()
        return config.valor if config else valor_default
    
    @staticmethod
    def set_valor(clave, valor, descripcion=''):
        """Establece el valor de una configuración"""
        config = Configuracion.query.filter_by(clave=clave).first()
        if config:
            config.valor = valor
            config.descripcion = descripcion
            config.fecha_actualizacion = datetime.utcnow()
        else:
            config = Configuracion(clave=clave, valor=valor, descripcion=descripcion)
            db.session.add(config)
        db.session.commit()
        return config

# Función para cargar usuarios (requerida por Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Configuración de WhatsApp
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID')
WHATSAPP_RECIPIENT = os.environ.get('WHATSAPP_RECIPIENT')  # Tu número de WhatsApp

def enviar_whatsapp(mensaje):
    """Envía un mensaje por WhatsApp usando la API de Twilio"""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID or not WHATSAPP_RECIPIENT:
        print("⚠️ Configuración de WhatsApp no encontrada. Mensaje simulado:")
        print(f"📱 WhatsApp: {mensaje}")
        return True
    
    try:
        url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": WHATSAPP_RECIPIENT,
            "type": "text",
            "text": {"body": mensaje}
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("✅ Mensaje enviado a WhatsApp exitosamente")
            return True
        else:
            print(f"❌ Error al enviar WhatsApp: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp: {str(e)}")
        return False

def enviar_whatsapp_cliente(numero_cliente, mensaje):
    """Envía un mensaje por WhatsApp directamente al cliente"""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        print("⚠️ Configuración de WhatsApp no encontrada. Mensaje simulado:")
        print(f"📱 WhatsApp a {numero_cliente}: {mensaje}")
        return True
    
    try:
        # Limpiar el número del cliente (remover espacios, guiones, etc.)
        numero_limpio = ''.join(filter(str.isdigit, numero_cliente))
        if not numero_limpio.startswith('51'):  # Si no tiene código de país, agregar Perú
            numero_limpio = '51' + numero_limpio
        
        url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": numero_limpio,
            "type": "text",
            "text": {"body": mensaje}
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Mensaje enviado a cliente {numero_cliente} exitosamente")
            return True
        else:
            print(f"❌ Error al enviar WhatsApp a cliente: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp a cliente: {str(e)}")
        return False

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('¡Bienvenido! Has iniciado sesión correctamente.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('admin'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validaciones
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('register.html')
        
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('register.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'error')
            return render_template('register.html')
        
        # Crear nuevo usuario
        user = Usuario(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Usuario creado exitosamente. Puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Rutas de la aplicación
@app.route('/')
def index():
    productos = Producto.query.filter_by(activo=True).all()
    categorias = Categoria.query.filter_by(activa=True).all()
    return render_template('index.html', productos=productos, categorias=categorias)


@app.route('/api/productos', methods=['GET'])
def get_productos():
    productos = Producto.query.filter_by(activo=True).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'precio': p.precio,
        'imagen': p.imagen,
        'stock': p.stock
    } for p in productos])

@app.route('/api/producto/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return jsonify({
        'success': True,
        'producto': {
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'imagen': producto.imagen,
            'stock': producto.stock,
            'activo': producto.activo
        }
    })

@app.route('/api/pedido', methods=['POST'])
def crear_pedido():
    try:
        data = request.json
        
        # Crear el pedido
        pedido = Pedido(
            cliente_nombre=data['cliente_nombre'],
            cliente_telefono=data['cliente_telefono'],
            cliente_direccion=data.get('cliente_direccion', ''),
            cliente_comentarios=data.get('cliente_comentarios', ''),
            total=data['total']
        )
        
        db.session.add(pedido)
        db.session.flush()  # Para obtener el ID del pedido
        
        # Crear los items del pedido y disminuir stock
        for item in data['items']:
            producto = Producto.query.get(item['producto_id'])
            if producto:
                # Validar que hay suficiente stock
                if producto.stock < item['cantidad']:
                    db.session.rollback()
                    return jsonify({
                        'success': False,
                        'error': f'No hay suficiente stock para {producto.nombre}. Stock disponible: {producto.stock}'
                    }), 400
                
                # Disminuir el stock
                producto.stock -= item['cantidad']
                
                # Crear el item del pedido
                pedido_item = PedidoItem(
                    pedido_id=pedido.id,
                    producto_id=item['producto_id'],
                    cantidad=item['cantidad'],
                    precio_unitario=producto.precio
                )
                db.session.add(pedido_item)
        
        db.session.commit()
        
        # Crear mensaje para WhatsApp
        mensaje = f"🛒 *NUEVO PEDIDO #{pedido.id}*\n\n"
        mensaje += f"👤 Cliente: {pedido.cliente_nombre}\n"
        mensaje += f"📞 Teléfono: {pedido.cliente_telefono}\n"
        mensaje += f"📍 Dirección: {pedido.cliente_direccion}\n"
        
        if pedido.cliente_comentarios:
            mensaje += f"💬 Comentarios: {pedido.cliente_comentarios}\n"
        
        mensaje += "\n📦 *Productos:*\n"
        
        for item in pedido.items:
            mensaje += f"• {item.producto.nombre} x{item.cantidad} - S/{item.precio_unitario * item.cantidad:.2f}\n"
            mensaje += f"  📊 Stock restante: {item.producto.stock}\n"
        
        mensaje += f"\n💰 *Total: S/{pedido.total:.2f}*\n"
        mensaje += f"📅 Fecha: {pedido.fecha_pedido.strftime('%d/%m/%Y %I:%M %p')}\n"
        mensaje += f"⏰ Hora: {pedido.fecha_pedido.strftime('%I:%M %p')}"
        
        # Enviar a WhatsApp
        enviar_whatsapp(mensaje)
        
        return jsonify({
            'success': True,
            'pedido_id': pedido.id,
            'mensaje': 'Pedido creado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pedido/<int:pedido_id>', methods=['GET'])
@login_required
def get_pedido(pedido_id):
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        return jsonify({
            'success': True,
            'pedido': pedido.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/producto', methods=['POST'])
@login_required
def crear_producto():
    try:
        data = request.json
        
        producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio=float(data['precio']),
            imagen=data.get('imagen', ''),
            stock=int(data.get('stock', 0)),
            categoria_id=data.get('categoria_id') if data.get('categoria_id') else None
        )
        
        db.session.add(producto)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'producto_id': producto.id,
            'mensaje': 'Producto creado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/producto/<int:producto_id>', methods=['PUT'])
@login_required
def editar_producto(producto_id):
    try:
        data = request.json
        producto = Producto.query.get_or_404(producto_id)
        
        # Solo actualizar los campos que se envían
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data.get('descripcion', '')
        if 'precio' in data:
            producto.precio = float(data['precio'])
        if 'imagen' in data:
            producto.imagen = data.get('imagen', '')
        if 'stock' in data:
            producto.stock = int(data.get('stock', 0))
        if 'activo' in data:
            producto.activo = bool(data.get('activo', True))
        if 'categoria_id' in data:
            producto.categoria_id = data.get('categoria_id') if data.get('categoria_id') else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': 'Producto actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/producto/<int:producto_id>', methods=['DELETE'])
@login_required
def eliminar_producto(producto_id):
    try:
        producto = Producto.query.get_or_404(producto_id)
        
        # Verificar si el producto tiene pedidos asociados
        pedidos_con_producto = PedidoItem.query.filter_by(producto_id=producto_id).count()
        
        if pedidos_con_producto > 0:
            # Si tiene pedidos, solo desactivar el producto
            producto.activo = False
            db.session.commit()
            return jsonify({
                'success': True,
                'mensaje': 'Producto desactivado (tiene pedidos asociados)'
            })
        else:
            # Si no tiene pedidos, eliminar completamente
            db.session.delete(producto)
            db.session.commit()
            return jsonify({
                'success': True,
                'mensaje': 'Producto eliminado exitosamente'
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== RUTAS DE CATEGORÍAS =====

@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    """Obtiene todas las categorías activas"""
    categorias = Categoria.query.filter_by(activa=True).all()
    return jsonify([categoria.to_dict() for categoria in categorias])

@app.route('/api/categoria/<int:categoria_id>', methods=['GET'])
def get_categoria(categoria_id):
    """Obtiene una categoría específica"""
    categoria = Categoria.query.get_or_404(categoria_id)
    return jsonify({
        'success': True,
        'categoria': categoria.to_dict()
    })

@app.route('/api/categoria', methods=['POST'])
@login_required
def crear_categoria():
    """Crea una nueva categoría"""
    try:
        data = request.json
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        icono = data.get('icono', 'fas fa-tag').strip()
        color = data.get('color', '#007bff').strip()
        
        if not nombre:
            return jsonify({
                'success': False,
                'error': 'El nombre de la categoría es obligatorio'
            }), 400
        
        # Verificar si ya existe una categoría con ese nombre
        if Categoria.query.filter_by(nombre=nombre).first():
            return jsonify({
                'success': False,
                'error': 'Ya existe una categoría con ese nombre'
            }), 400
        
        categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion,
            icono=icono,
            color=color
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': 'Categoría creada exitosamente',
            'categoria': categoria.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categoria/<int:categoria_id>', methods=['PUT'])
@login_required
def editar_categoria(categoria_id):
    """Edita una categoría existente"""
    try:
        data = request.json
        categoria = Categoria.query.get_or_404(categoria_id)
        
        # Solo actualizar los campos que se envían
        if 'nombre' in data:
            categoria.nombre = data['nombre']
        if 'descripcion' in data:
            categoria.descripcion = data.get('descripcion', '')
        if 'icono' in data:
            categoria.icono = data.get('icono', 'fas fa-tag')
        if 'color' in data:
            categoria.color = data.get('color', '#007bff')
        if 'activa' in data:
            categoria.activa = bool(data.get('activa', True))
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': 'Categoría actualizada exitosamente',
            'categoria': categoria.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categoria/<int:categoria_id>', methods=['DELETE'])
@login_required
def eliminar_categoria(categoria_id):
    """Elimina una categoría"""
    try:
        categoria = Categoria.query.get_or_404(categoria_id)
        
        # Verificar si tiene productos asociados
        if categoria.productos:
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar la categoría porque tiene productos asociados'
            }), 400
        
        db.session.delete(categoria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': 'Categoría eliminada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pedido/<int:pedido_id>/estado', methods=['PUT'])
@login_required
def actualizar_estado_pedido(pedido_id):
    try:
        data = request.json
        pedido = Pedido.query.get_or_404(pedido_id)
        pedido.estado = data['estado']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': 'Estado actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pedido/<int:pedido_id>/confirmar', methods=['POST'])
@login_required
def confirmar_pedido(pedido_id):
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        # Actualizar estado del pedido a confirmado
        pedido.estado = 'confirmado'
        db.session.commit()
        
        # Crear mensaje de confirmación para el cliente
        mensaje_cliente = f"✅ *PEDIDO CONFIRMADO #{pedido.id}*\n\n"
        mensaje_cliente += f"¡Hola {pedido.cliente_nombre}!\n\n"
        mensaje_cliente += f"Tu pedido ha sido *confirmado* y está siendo preparado.\n\n"
        mensaje_cliente += f"📋 *Resumen de tu pedido:*\n"
        
        for item in pedido.items:
            mensaje_cliente += f"• {item.producto.nombre} x{item.cantidad} - S/{item.precio_unitario * item.cantidad:.2f}\n"
        
        mensaje_cliente += f"\n💰 *Total: S/{pedido.total:.2f}*\n"
        mensaje_cliente += f"📍 *Dirección de entrega:* {pedido.cliente_direccion}\n"
        mensaje_cliente += f"📅 *Fecha del pedido:* {pedido.fecha_pedido.strftime('%d/%m/%Y %I:%M %p')}\n\n"
        
        if pedido.cliente_comentarios:
            mensaje_cliente += f"💬 *Tus comentarios:* {pedido.cliente_comentarios}\n\n"
        
        mensaje_cliente += f"🚚 *Estado:* Confirmado - En preparación\n"
        mensaje_cliente += f"⏰ *Tiempo estimado:* 30-45 minutos\n\n"
        mensaje_cliente += f"¡Gracias por elegirnos! Te contactaremos cuando esté listo para entrega. 😊"
        
        # Enviar mensaje al cliente
        enviar_whatsapp_cliente(pedido.cliente_telefono, mensaje_cliente)
        
        return jsonify({
            'success': True,
            'mensaje': 'Pedido confirmado y mensaje enviado al cliente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notificaciones/pedidos', methods=['GET'])
@login_required
def get_notificaciones_pedidos():
    """Obtiene el contador de pedidos pendientes para notificaciones"""
    try:
        pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').count()
        pedidos_confirmados = Pedido.query.filter_by(estado='confirmado').count()
        total_pendientes = pedidos_pendientes + pedidos_confirmados
        
        # Obtener el último pedido para mostrar información adicional
        ultimo_pedido = Pedido.query.order_by(Pedido.fecha_pedido.desc()).first()
        
        return jsonify({
            'success': True,
            'pedidos_pendientes': pedidos_pendientes,
            'pedidos_confirmados': pedidos_confirmados,
            'total_pendientes': total_pendientes,
            'ultimo_pedido': {
                'id': ultimo_pedido.id if ultimo_pedido else None,
                'cliente_nombre': ultimo_pedido.cliente_nombre if ultimo_pedido else None,
                'total': ultimo_pedido.total if ultimo_pedido else None,
                'fecha_pedido': ultimo_pedido.fecha_pedido.isoformat() if ultimo_pedido and ultimo_pedido.fecha_pedido else None,
                'estado': ultimo_pedido.estado if ultimo_pedido else None
            } if ultimo_pedido else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pedido/<int:pedido_id>', methods=['DELETE'])
@login_required
def eliminar_pedido(pedido_id):
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        # Eliminar todos los items del pedido primero
        for item in pedido.items:
            db.session.delete(item)
        
        # Eliminar el pedido
        db.session.delete(pedido)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': 'Pedido eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configuracion', methods=['GET'])
@login_required
def get_configuracion():
    """Obtiene la configuración actual de la tienda"""
    try:
        nombre_tienda = Configuracion.get_valor('nombre_tienda', 'Mi Tienda Online')
        descripcion_tienda = Configuracion.get_valor('descripcion_tienda', '')
        whatsapp_admin = Configuracion.get_valor('whatsapp_admin', '')
        
        # Obtener fecha de última actualización
        config_nombre = Configuracion.query.filter_by(clave='nombre_tienda').first()
        ultima_actualizacion = config_nombre.fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if config_nombre and config_nombre.fecha_actualizacion else '-'
        
        return jsonify({
            'success': True,
            'configuracion': {
                'nombre_tienda': nombre_tienda,
                'descripcion_tienda': descripcion_tienda,
                'whatsapp_admin': whatsapp_admin,
                'ultima_actualizacion': ultima_actualizacion
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configuracion', methods=['POST'])
@login_required
def update_configuracion():
    """Actualiza la configuración de la tienda"""
    try:
        data = request.json
        nombre_tienda = data.get('nombre_tienda', '').strip()
        descripcion_tienda = data.get('descripcion_tienda', '').strip()
        whatsapp_admin = data.get('whatsapp_admin', '').strip()
        
        if not nombre_tienda:
            return jsonify({
                'success': False,
                'error': 'El nombre de la tienda es obligatorio'
            }), 400
        
        # Guardar configuración
        Configuracion.set_valor('nombre_tienda', nombre_tienda, 'Nombre de la tienda que aparece en el encabezado')
        Configuracion.set_valor('descripcion_tienda', descripcion_tienda, 'Descripción de la tienda que aparece en la página principal')
        Configuracion.set_valor('whatsapp_admin', whatsapp_admin, 'Número de WhatsApp del administrador para contacto')
        
        # Obtener fecha de actualización
        config_nombre = Configuracion.query.filter_by(clave='nombre_tienda').first()
        ultima_actualizacion = config_nombre.fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if config_nombre and config_nombre.fecha_actualizacion else '-'
        
        return jsonify({
            'success': True,
            'mensaje': 'Configuración actualizada exitosamente',
            'ultima_actualizacion': ultima_actualizacion
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configuracion/publica', methods=['GET'])
def get_configuracion_publica():
    """Obtiene la configuración pública de la tienda (sin login)"""
    try:
        nombre_tienda = Configuracion.get_valor('nombre_tienda', 'Mi Tienda Online')
        descripcion_tienda = Configuracion.get_valor('descripcion_tienda', '')
        whatsapp_admin = Configuracion.get_valor('whatsapp_admin', '')
        
        return jsonify({
            'success': True,
            'configuracion': {
                'nombre_tienda': nombre_tienda,
                'descripcion_tienda': descripcion_tienda,
                'whatsapp_admin': whatsapp_admin
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cambiar-password', methods=['POST'])
@login_required
def cambiar_password():
    """Cambia la contraseña del usuario actual"""
    try:
        data = request.json
        password_actual = data.get('password_actual', '').strip()
        password_nueva = data.get('password_nueva', '').strip()
        password_confirmar = data.get('password_confirmar', '').strip()
        
        # Validaciones
        if not password_actual:
            return jsonify({
                'success': False,
                'error': 'La contraseña actual es obligatoria'
            }), 400
        
        if not password_nueva:
            return jsonify({
                'success': False,
                'error': 'La nueva contraseña es obligatoria'
            }), 400
        
        if len(password_nueva) < 6:
            return jsonify({
                'success': False,
                'error': 'La nueva contraseña debe tener al menos 6 caracteres'
            }), 400
        
        if password_nueva != password_confirmar:
            return jsonify({
                'success': False,
                'error': 'Las contraseñas nuevas no coinciden'
            }), 400
        
        # Verificar contraseña actual
        if not current_user.check_password(password_actual):
            return jsonify({
                'success': False,
                'error': 'La contraseña actual es incorrecta'
            }), 400
        
        # Cambiar contraseña
        current_user.set_password(password_nueva)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': 'Contraseña cambiada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== RUTAS PRINCIPALES =====

@app.route('/')
def tienda_index():
    """Página principal de la tienda"""
    productos = Producto.query.filter_by(activo=True).all()
    categorias = Categoria.query.filter_by(activa=True).all()
    return render_template('index.html', productos=productos, categorias=categorias)

@app.route('/terms')
def terms():
    """Página de términos y condiciones"""
    return render_template('terms.html')

@app.route('/admin')
@login_required
def panel_admin():
    """Panel de administración"""
    productos = Producto.query.all()
    pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    usuarios = Usuario.query.all()
    categorias = Categoria.query.all()
    
    # Debug: imprimir categorías
    print(f"DEBUG ADMIN: Categorías encontradas: {len(categorias)}")
    for cat in categorias:
        print(f"  - {cat.nombre} (ID: {cat.id}, Activa: {cat.activa})")
    
    # Estadísticas para la configuración
    productos_activos = Producto.query.filter_by(activo=True).count()
    total_pedidos = Pedido.query.count()
    total_usuarios = Usuario.query.count()
    total_categorias = Categoria.query.filter_by(activa=True).count()
    
    return render_template('admin.html', 
                         productos=productos, 
                         pedidos=pedidos,
                         categorias=categorias,
                         productos_activos=productos_activos,
                         total_pedidos=total_pedidos,
                         total_usuarios=total_usuarios,
                         total_categorias=total_categorias)

@app.route('/login', methods=['GET', 'POST'])
def login_usuario():
    """Página de login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('panel_admin'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def registro_usuario():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
        elif Usuario.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'error')
        elif Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
        else:
            user = Usuario(username=username, email=email, es_admin=False)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('login_usuario'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout_usuario():
    """Cerrar sesión"""
    logout_user()
    return redirect(url_for('tienda_index'))

# Crear las tablas de la base de datos
with app.app_context():
    db.create_all()
    
    # Crear usuario administrador por defecto si no existe
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
    
    # Agregar algunas categorías de ejemplo si no existen
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
    
    # Agregar algunos productos de ejemplo si no existen
    if Producto.query.count() == 0:
        # Obtener las categorías creadas para asignarlas a los productos
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

if __name__ == '__main__':
    print("🚀 Iniciando servidor...")
    print("📱 Asegúrate de configurar las variables de entorno para WhatsApp")
    print("🌐 La aplicación estará disponible en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
