heroku create --stack cedar --buildpack http://github.com/heroku/heroku-buildpack-c.git
heroku addons:add mongolab

git push heroku master
echo 'export WORKON_HOME=~/environments' >> .bashrc # Change this directory if you don't like it
echo '. /usr/local/bin/virtualenvwrapper.sh' >> .bashrc