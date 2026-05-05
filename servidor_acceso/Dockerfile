FROM php:8.1-apache

# Instalar extensiones de PHP necesarias para MySQL
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Habilitar mod_rewrite (necesario para las rutas de api.php/check)
RUN a2enmod rewrite

# Configurar Apache para servir index.php por defecto
RUN sed -i 's/DirectoryIndex .*/DirectoryIndex index.php index.html/g' /etc/apache2/mods-enabled/dir.conf

# --- CORRECCIÓN AQUÍ ---
# Copiamos directamente desde 'src/' porque ya no existe 'src/php/'
COPY src/ /var/www/html/

# Cambiar permisos para que Apache pueda leer los archivos
RUN chown -R www-data:www-data /var/www/html/

# Exponer el puerto 80 dentro del contenedor
EXPOSE 80