heroku create --stack cedar --buildpack http://github.com/heroku/heroku-buildpack-c.git
git push heroku master
mkvirtualenv listsurf
#deactivate

workon listsurf
./listsurf.py