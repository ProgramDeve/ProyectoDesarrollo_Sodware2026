FROM php:8.2-apache
# Habilitar mod_rewrite y extensiones comunes
RUN docker-php-ext-install mysqli pdo pdo_mysql
COPY . /var/www/html/
WORKDIR /var/www/html/
EXPOSE 80
