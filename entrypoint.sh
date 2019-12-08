#!/bin/bash
### entrypoint.sh
### to be run as the ENTRYPOINT within a container

if [[ -z "$update_flag" ]]; then
    ./tweet_generator.py -a ${account} -e ${epochs} -c ${tweet_count} 
else
    ./tweet_generator.py -a ${account} -e ${epochs} -c ${tweet_count} -u
fi