ssh-keygen -A
/usr/sbin/sshd -D  &
pip install pydevd-pycharm~=223.8836.34
sleep 1
uwsgi  --py-autoreload=1 --http 0.0.0.0:$PORT --module wsgi:application   --workers 1 --threads 6   --enable-threads --skip-atexit-teardown --max-worker-lifetime=200000--max-worker-lifetime-delta=200000 --harakiri=200000 -b 32768
