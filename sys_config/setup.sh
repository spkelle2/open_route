#!/bin/bash

# run with sudo - make sure to set sean/ubuntu in all files
# %s/sean/ubuntu/gc - change user in setup files
# to get sock file: make sure paths in nginx, open_route.conf and gunicorn
# start are correct

# install needed ubuntu packages
apt-get install gcc nginx supervisor

# install conda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# install conda env
conda env create -f ../env_or.yml

# move supervisor file to conf.d folder
cp open_route.conf /etc/supervisor/conf.d/

# make sure supervisor comes up after reboot
systemctl enable supervisor

# make sure supervisor starts now
systemctl start supervisor

# have supervisor reread the conf files and restart apps with changed confs
supervisorctl reread
supervisorctl update

# move nginx to sites-available
cp open_route /etc/nginx/sites-available/

# make link to sites enabled
ln -s /etc/nginx/sites-available/open_route /etc/nginx/sites-enabled/open_route

# reset nginx
service nginx restart
