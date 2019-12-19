FROM python:3.7.5

# Install cron
RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

#CMD [ "python", "./bot.py" ]
ENTRYPOINT "/usr/src/app/entrypoint.sh"