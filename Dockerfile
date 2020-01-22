FROM python:3
WORKDIR home
ADD main.py .
ADD settings/settings.py settings/
ADD decorators.py .
ADD data.py .
VOLUME /home/settings/

RUN pip install python-telegram-bot
RUN pip install requests
RUN pip install peewee
RUN pip install validators

RUN mkdir data
VOLUME /home/data/

CMD [ "python","-u","./main.py"]
