FROM python:3.12

ENV HOME /root

WORKDIR /root

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

# CMD ["gunicorn", "-w", "1", "--threads", "12", "-b", "0.0.0.0:8000", "--timeout", "120", "--chdir", "src/serverFiles/", "server:app"]
#CMD ["/wait", "&&", "gunicorn", "-b", "0.0.0.0:8000", "--timeout", "120", "--chdir", "src/serverFiles/", "server:app"]
CMD /wait && gunicorn -k gevent --worker-connections 1000 -b 0.0.0.0:8000 --timeout 120 --chdir src/serverFiles server:app