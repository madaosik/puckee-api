FROM python:3.9.1
EXPOSE 5000
RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/requirements.txt
RUN pip install -r requirements.txt
COPY . /api
COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
#RUN chmod +x ./entrypoint.sh
#ENTRYPOINT["ls", "-l"]
#ENTRYPOINT ["bash", "./entrypoint.sh"]
# By default run entrypoint.sh, but if command-line arguments are given run those instead:
#CMD ./entrypoint.sh
