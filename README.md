# ShitpostBot

## Configuration
Install dependencies:
```shell script
pip3 install -r requirements.txt
```

Create and fill out the required configuration file before doing anyting:
```shell script
cp utils/SAMPLE.config.ini utils/config.ini
vim utils/config.ini
```

Create the tweet table:
```shell script
psql -h <host> -d <database> -U <user> -a -f utils/sql/tweet.ddl.sql
```

## Scripts
### scraper.py
Scrapes all of the tweets from [this site](https://cooltweets.herokuapp.com/) 
and inserts them into a json file.
```shell script
./scraper.py [-o, --output-file] [-nl, --no-logging]
```