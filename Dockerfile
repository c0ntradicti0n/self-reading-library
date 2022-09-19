FROM  c0ntradicti0n/pdf2htmlex:0.18.8.rc2-x-tag-feature-file-css-20220911-ubuntu-22.04-x86_64
RUN apt install python3-pip -y
RUN apt install git -y

WORKDIR /home/finn/Programming/self-reading-library

COPY python .

RUN pip install torch
RUN pip install -r requirements.txt

ENTRYPOINT uwsgi --http 0.0.0.0:9999 --module wsgi:application --memory-report  --workers 16 --threads 2  --memory-report --enable-threads --skip-atexit-teardown --max-worker-lifetime=300 --max-worker-lifetime-delta=320 --harakiri=500

