echo "source ~/.bashrc"
workon listsurf
m2sh load -config mongrel2.conf -db the.db
m2sh start -db the.db -every