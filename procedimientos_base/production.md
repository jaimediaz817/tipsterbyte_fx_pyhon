# ¿Cómo funciona?
- En lugar de un archivo, inyectarás las variables de entorno en el contenedor en el momento del despliegue. La plataforma se encarga de esto.

## En un servidor Linux simple con Docker: Podrías definir las variables de entorno antes de ejecutar el comando:

export POSTGRES_USER="usuario_prod"
export POSTGRES_PASSWORD="password_super_seguro_de_prod"
export POSTGRES_DB="db_prod"
docker-compose up -d