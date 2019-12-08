# ShitpostBot


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

Scrape tweets:
```shell script
./scripts/scraper.py -o <output json file path>
```

Load tweets:
```shell script
./scripts/tweet2db.py -f <input json file path>
```

## Generating Tweets
Locally:
```shell script
./scripts/tweet_generator.py -a <account> -c <number of tweets to generate>
```

Docker:
```shell script
# relies on settings in .env file!
docker-compose up --build
```

*Note: you may need to increase your allocated RAM for the Docker daemon to run this. Tensorflow uses a decent chunk of memory.*

## Scripts
### scraper.py
Scrapes all of the tweets from [this site](https://cooltweets.herokuapp.com/) 
and inserts them into a ```json``` file.
```shell script
./scripts/scraper.py [-o, --output-file] [-nl, --no-logging]
```

### tweet2db.py
Takes in a ```json``` file (produced by ```scraper.py```) and inserts it into PostgreSQL.
```shell script
./scripts/tweet2db.py [-f, --file-path] [-n, --chunk-size]
```

### tweet_generator
Generates a tweet in the style of the given account. Generates a odel for the account if it doesn't already exist in the database. 
```shell script
./scripts/tweet_generator.py [-a, --acount] [-c, --count] [-e, --epochs] [-u, --update-model]
```