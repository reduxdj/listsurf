pip install virtualenv
brew install mongrel2
brew install 
brew install zeromq

mongod
mkvirtualenv listsurf
#deactivate
git clone git://github.com/j2labs/brubeck.git
git clone git://github.com/j2labs/listsurf.git
pip install virtualenv virtualenvwrapper
export WORKON_HOME="~/.virtualenvs"
source /usr/local/bin/virtualenvwrapper.sh
brew install sqlite sqlite3 sqlite-dev
m2sh load -config mongrel2.conf -db config.db
m2sh start -db config.db -every
pip install -I -r ./envs/brubeck.reqs
pip install -I -r ./envs/eventlet.reqs
pip install -I -r ./envs/gevent.reqs
workon listsurf
./listsurf.py
