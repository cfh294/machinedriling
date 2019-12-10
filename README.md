# machinedriling
A ```gpt-2```-backed bot that posts generated tweets in the style of [@dril]([http](https://twitter.com/dril)). @dril tweets were scraped using [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and stored in a ```PostgreSQL``` database. All database-related code 
utilizes [SQLAlchemy](https://www.sqlalchemy.org/). 

Based on https://github.com/minimaxir/gpt-2-simple

## Configuration

#### Local Configuration
Install dependencies:
```shell script
pip3 install -r requirements.txt
```

Create and fill out the required configuration file before doing anyting else:
```shell script
cp ./SAMPLE.env .env 
```

#### Database Setup
Configure your ```.pgpass``` file to have an entry for the PostgreSQL host. Use ```wtm``` as the database. Instructions can be found [here](https://www.postgresql.org/docs/9.3/libpq-pgpass.html). 

Create the necessary tables (if needed):
```shell script
./scripts/setup.sh <database host> <database user> <database name>
```

## Scripts

### scraper.py
```shell script
./scripts/scraper.py [-u, --user] [-nl, --no-logging]
```

### bot.py
Generates a string of tweets. 
```shell script
./scripts/bot.py
```

### get_tweet_txt.py 
Converts a list of tweets to an output ```.txt``` file. 
```shell script 
./scripts/get_tweet_txt.py [-u, --user] [-f, --file]
```