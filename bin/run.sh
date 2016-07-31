uwsgi --plugin python --wsgi-file bin/alignak_webui.py --callable app --socket 0.0.0.0:5001 --protocol=http --enable-threads -p 1
