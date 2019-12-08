#!/bin/bash
### docker-entrypoint.sh
### to be run as the ENTRYPOINT within a container

# Check APP_ENVIRONMENT
if [[ -z "$update_flag" ]]; then
    ./model_generator.py -a ${account} -e ${epochs} -c 10 -u
else
    ./model_generator.py -a ${account} -e ${epochs} -c 10
fi