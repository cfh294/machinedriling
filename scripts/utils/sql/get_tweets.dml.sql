select *
from wtm.tweet
where tweet_user=%(in_user)s;