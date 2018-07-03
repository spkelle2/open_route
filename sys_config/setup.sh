#!/bin/bash

# run with sudo - make sure to set sean/ubuntu in all files

# install needed ubuntu packages
apt-get install gcc nginx supervisor

# move supervisor file to conf.d folder and update supervisor
cp open_route.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update

# move nginx to sites-available
cp open_route /etc/nginx/sites-available/

# make link to sites enabled
ln -s /etc/nginx/sites-available/open_route /etc/nginx/sites-enabled/open_route

# reset nginx
service nginx restart
