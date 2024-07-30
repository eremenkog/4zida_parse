FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y cron supervisor && \
    pip install --no-cache-dir telebot pandas bs4 python-dotenv
    


WORKDIR /app
COPY . /app

RUN python /app/4zida_parse.py
RUN echo "0 * * * * python /app/4zida_parse.py >> /var/log/cron.log 2>&1" > /etc/cron.d/4zida_parse
RUN chmod 0644 /etc/cron.d/4zida_parse
RUN crontab /etc/cron.d/4zida_parse

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]