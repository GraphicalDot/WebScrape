#!/bin/bash

sudo apt-get update
apt-get install tor
sudo /etc/init.d/tor restart
sudo cp configs/tor.config  /etc/tor/torrc
sudo /etc/init.d/tor restart




apt-get install git
apt-get install python-dev python-pip
git clone git://github.com/aaronsw/pytorctl.git
sudo pip install pytorctl/


sudo apt-get install privoxy
sudo cp configs/privoxy_config.config  /etc/privoxy/config
sudo /etc/init.d/privoxy restart

##If not run this command, the user:group of this file will be debian+-:debian+-
sudo chown kmama02:kmama02 /var/run/tor/control.authcookie 
