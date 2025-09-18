# Instrucciones para Desplegar en PythonAnywhere

## 1. Crear cuenta en PythonAnywhere
- Ve a https://www.pythonanywhere.com/
- Crea una cuenta gratuita o de pago

## 2. Configurar Base de Datos MySQL
1. En el dashboard de PythonAnywhere, ve a la pestaña "Databases"
2. Crea una nueva base de datos MySQL
3. Anota el nombre de usuario, contraseña y nombre de la base de datos
hugo010996
## 3. Subir archivos
1. Ve a la pestaña "Files"
2. Sube todos los archivos de tu proyecto:
   - app.py
   - wsgi.py
   - requirements.txt
   - templates/ (carpeta completa)
   - static/ (carpeta completa)
   - config_pythonanywhere.txt (renómbralo a .env)

## 4. Instalar dependencias
1. Ve a la pestaña "Consoles"
2. Abre una consola Bash
3. Ejecuta:
```bash
pip3.10 install --user -r requirements.txt
```

## 5. Configurar variables de entorno
1. Edita el archivo .env con tus datos reales:
```bash
nano .env
```
2. Actualiza la DATABASE_URL con tus datos de MySQL:
```
DATABASE_URL=mysql+pymysql://tu_usuario:tu_password@mysql.server/tu_usuario$nombre_base_datos
```

## 6. Configurar aplicación web
1. Ve a la pestaña "Web"
2. Haz clic en "Add a new web app"
3. Selecciona "Flask"
4. Selecciona Python 3.10
5. En "Source code", pon la ruta a tu archivo wsgi.py
6. En "WSGI configuration file", edita el archivo y asegúrate de que apunte a tu wsgi.py

## 7. Inicializar base de datos
1. En la consola, ejecuta:
```bash
python3.10 app.py
```
Esto creará las tablas y el usuario admin por defecto.

## 8. Acceder a tu aplicación
- Tu aplicación estará disponible en: https://tu_usuario.pythonanywhere.com/
- Usuario admin: admin
- Contraseña: admin123 (¡cámbiala inmediatamente!)

## Notas importantes:
- Cambia la contraseña del admin en producción
- Configura las variables de WhatsApp si las usas
- La cuenta gratuita tiene limitaciones de tráfico
- Considera actualizar a una cuenta de pago para producción
