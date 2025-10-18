PROJECT



sudo chown -R sophiessa:sophiessa /var/www/4kara.com/html
sudo chown -R www-data:www-data /var/www/4kara.com/html
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl restart gunicorn.service
sudo systemctl status gunicorn.service
sudo systemctl status nginx