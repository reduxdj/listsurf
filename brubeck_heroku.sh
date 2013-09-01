#!/bin/bash
#
# Note: This is the only file you *really* need. I've copied the contents
#   of the important files that are part of our git repo for easier reading 
#   below :)
# 
# I've prefixed this file with two dots to make it rise to the top of the 
# gist. you can ignore those
#
cd ~
git clone https://github.com/j2labs/brubeck.git
git clone https://github.com/zedshaw/mongrel2.git
wget http://download.zeromq.org/zeromq-3.2.2.tar.gz
./autogen.sh
./configure  ## for mac ports use: ./configure --prefix=/opt/local
make
sudo make install
tar zxf zeromq-3.2.2.tar.gz
# Create and enter a virtualenv called "listsurf"
mkvirtualenv listsurf --no-site-packages
workon listsurf

cd ~/Desktop/mongrel2
make  ## for mac ports use: make macports
mkdir myapp
cd myapp
sudo apt-get install sqlite3
# Install the dependencies and throw it in a requirements file (used by heroku)
pip install git+git://github.com/j2labs/brubeck.git dictshield ujson gevent gunicorn
pip freeze > requirements.txt
 
# This is a basic app
cat << EOF > app.py
from brubeck.request_handling import Brubeck, WebMessageHandler
from brubeck.connections import WSGIConnection
 
class DemoHandler(WebMessageHandler):
    def get(self):
        self.set_body("Hello, from Brubeck!")
        return self.render()
 
config = {
    'msg_conn': WSGIConnection(),
    'handler_tuples': [
        (r'^/', DemoHandler)
    ]
}
 
app = Brubeck(**config)
 
# This is the wsgi handler used by gunicorn
def application(environ, callback): 
    return app.msg_conn.process_message(app, environ, callback)
EOF
 
# Tell heroku how to run it
cat << EOF > Procfile
web: gunicorn app --bind "0.0.0.0:\$PORT" --workers 3
EOF
 
cat << EOF > .gitignore
*.pyc
EOF
 
# create a git repo for the code so we can push it into heroku
git init .
git add .
git commit -a -m "initial commit"
 
# create the heroku app and push our app into it
heroku create --stack cedar
git push heroku master
 
# open the site we just created
heroku open