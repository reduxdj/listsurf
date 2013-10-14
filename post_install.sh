#debian, upgrades debian to latest and creates an install, forces update no nags
unset UCF_FORCE_CONFFOLD
export UCF_FORCE_CONFFNEW=YES
ucf --purge /boot/grub/menu.lst

echo "deb http://ftp.de.debian.org/debian/ stable main 
deb-src http://ftp.de.debian.org/debian/ stable main 
deb http://ftp.de.debian.org/debian/ stable main 
deb-src http://ftp.de.debian.org/debian/ stable main 
deb http://www.debian-multimedia.org/ stable main" > /etc/apt/sources.list

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy dist-upgrade
apt-get -y install mongodb
apt-get -y install python-dev
apt-get -y install make
apt-get -y install git
apt-get -y install sqlite3
apt-get -y install gcc
apt-get -y install libsqlite3-dev
apt-get -y install python-pip
pip install -I brubeck
pip install pymongo
pip install python-bcrypt
pip install python-dateutil
pip install pyzmq
pip install eventlet
pip install jinja2
pip install ujson
pip install --no-index -f http://dist.plone.org/thirdparty/ -U PIL
easy_install http://dist.plone.org/thirdparty/PIL-1.1.7.tar.gz
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 6767
wget https://github.com/zedshaw/mongrel2/tarball/v1.8.0
cd v1.8.0 && ./configure && make clean all && make install
git clone https://github.com/reduxdj/listsurf
cd "~/listsurf/" && ./listsurf.py
useradd -m -d /home/web -s /bin/bash -c "the web owner" -U web
echo "web ALL=(ALL:ALL) ALL" >> /etc/sudoers
#mkdir -p proc && sudo mount --bind /proc proc