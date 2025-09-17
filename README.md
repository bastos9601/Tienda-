# 🛒 Sistema de Pedidos con WhatsApp

Un sistema completo de tienda online que permite a los clientes realizar pedidos y recibir notificaciones por WhatsApp.

## ✨ Características

- 🛍️ **Catálogo de productos** con interfaz web moderna
- 🛒 **Carrito de compras** interactivo
- 📱 **Integración con WhatsApp** para notificaciones automáticas
- 👨‍💼 **Panel de administración** con autenticación segura
- 🔐 **Sistema de usuarios** con login/logout
- 💾 **Base de datos SQLite** para almacenar información
- 🌐 **Multiplataforma** - funciona en Windows, Mac y Linux

## 🚀 Instalación y Configuración

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
cp config.env.example .env
```

Edita el archivo `.env` con tus datos:

```env
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
WHATSAPP_TOKEN=tu-token-de-whatsapp-business
WHATSAPP_PHONE_ID=tu-phone-id-de-whatsapp
WHATSAPP_RECIPIENT=+1234567890
```

### 3. Configurar WhatsApp Business API

1. Ve a [Facebook Developers](https://developers.facebook.com/)
2. Crea una nueva aplicación
3. Configura WhatsApp Business API
4. Obtén tu token de acceso y Phone ID
5. Agrega tu número de WhatsApp como destinatario

### 4. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 📱 Uso del Sistema

### Para Clientes
1. Visita `http://localhost:5000`
2. Explora los productos disponibles
3. Agrega productos al carrito
4. Completa tus datos de contacto
5. Realiza el pedido
6. Recibe confirmación por WhatsApp

### Para Administradores
1. Visita `http://localhost:5000/login`
2. Inicia sesión con las credenciales por defecto:
   - **Usuario:** `admin`
   - **Contraseña:** `admin123`
3. Accede al panel de administración
4. Gestiona productos (agregar, editar, eliminar)
5. Revisa y actualiza el estado de pedidos
6. Ve detalles completos de cada pedido
7. Crea nuevos usuarios administradores

## 🗂️ Estructura del Proyecto

```
emprendimiento/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias de Python
├── config.env.example    # Ejemplo de configuración
├── README.md             # Este archivo
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── index.html        # Página principal
│   ├── admin.html        # Panel de administración
│   ├── login.html        # Página de login
│   └── register.html     # Página de registro
└── static/               # Archivos estáticos (CSS, JS, imágenes)
```

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python, Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de datos**: SQLite
- **Autenticación**: Flask-Login, Werkzeug Security
- **WhatsApp**: Facebook Graph API
- **Iconos**: Font Awesome

## 📊 Base de Datos

El sistema crea automáticamente las siguientes tablas:

- **Productos**: Información de productos disponibles
- **Pedidos**: Datos de pedidos realizados
- **PedidoItems**: Items específicos de cada pedido
- **Usuarios**: Cuentas de administradores con autenticación

## 🔧 Personalización

### Agregar nuevos productos
Usa el panel de administración o modifica directamente en la base de datos.

### Cambiar el diseño
Edita los archivos en la carpeta `templates/` y `static/`.

### Modificar notificaciones de WhatsApp
Edita la función `enviar_whatsapp()` en `app.py`.

### Cambiar credenciales de administrador
1. Inicia sesión con las credenciales por defecto
2. Ve a la página de registro para crear un nuevo usuario
3. Inicia sesión con el nuevo usuario
4. Elimina el usuario `admin` por defecto (opcional)

## 🚨 Solución de Problemas

### WhatsApp no funciona
- Verifica que las variables de entorno estén configuradas correctamente
- Asegúrate de que tu token de WhatsApp sea válido
- Revisa que el número de teléfono esté en formato internacional (+1234567890)

### Error de base de datos
- Elimina el archivo `tienda.db` para recrear la base de datos
- Verifica que SQLite esté instalado correctamente

### Puerto ocupado
- Cambia el puerto en la línea final de `app.py`
- Ejemplo: `app.run(debug=True, host='0.0.0.0', port=8000)`

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa la documentación de Flask
2. Consulta la documentación de WhatsApp Business API
3. Verifica que todas las dependencias estén instaladas correctamente

## 🔄 Actualizaciones Futuras

- [ ] Sistema de usuarios y autenticación
- [ ] Integración con pasarelas de pago
- [ ] Notificaciones por email
- [ ] Reportes y estadísticas
- [ ] App móvil nativa
- [ ] Integración con redes sociales

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

¡Disfruta tu nueva tienda online! 🎉
