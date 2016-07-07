uwsgi --plugin python --wsgi-file alignak_webui.py --callable app --socket 0.0.0.0:8868 --protocol=http --enable-threads
