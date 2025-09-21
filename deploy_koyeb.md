# Guía de Despliegue en Koyeb

## Pasos para desplegar tu aplicación en Koyeb

### 1. Preparar el repositorio
```bash
# Asegúrate de que todos los archivos estén en tu repositorio Git
git add .
git commit -m "Configuración para Koyeb"
git push origin main
```

### 2. Crear cuenta en Koyeb
1. Ve a [koyeb.com](https://koyeb.com)
2. Crea una cuenta o inicia sesión
3. Conecta tu cuenta de GitHub

### 3. Desplegar la aplicación
1. En el dashboard de Koyeb, haz clic en "Create Service"
2. Selecciona "GitHub" como fuente
3. Elige tu repositorio
4. Koyeb detectará automáticamente el archivo `koyeb.yaml`
5. Haz clic en "Deploy"

### 4. Configurar variables de entorno
En el dashboard de Koyeb, ve a tu servicio y configura estas variables:

- `WHATSAPP_TOKEN`: Tu token de WhatsApp Business API
- `WHATSAPP_PHONE_ID`: Tu Phone ID de WhatsApp
- `WHATSAPP_RECIPIENT`: Número de teléfono de destino (formato: 51999999999)

### 5. Verificar el despliegue
- La base de datos PostgreSQL se creará automáticamente
- Tu aplicación estará disponible en la URL proporcionada por Koyeb
- Los logs se pueden ver en el dashboard de Koyeb

## Archivos importantes para Koyeb

- `koyeb.yaml`: Configuración del servicio y base de datos
- `requirements.txt`: Dependencias de Python
- `app.py`: Aplicación principal con configuración de base de datos
- `gunicorn`: Servidor WSGI para producción

## Comandos útiles

```bash
# Ver logs en tiempo real
koyeb logs --service tu-servicio

# Actualizar el servicio
git push origin main  # Koyeb detectará automáticamente los cambios

# Escalar el servicio
# Ve al dashboard de Koyeb y ajusta el plan según necesites
```

## Solución de problemas

### Error de conexión a la base de datos
- Verifica que `DATABASE_URL` esté configurada correctamente
- Asegúrate de que la base de datos esté en la misma región

### Error de dependencias
- Verifica que `requirements.txt` tenga todas las dependencias
- Revisa los logs de build en Koyeb

### Error de puerto
- Koyeb usa la variable `PORT` automáticamente
- Asegúrate de que gunicorn esté configurado para usar `0.0.0.0:$PORT`
