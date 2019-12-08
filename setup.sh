#!/bin/bash
set -e
if [[ -z "$1" ]]; then
    echo "Missing host."
    exit 1
fi
if [[ -z "$2" ]]; then 
    echo "Missing user."
    exit 1
fi
if [[ -z "$3" ]]; then 
    echo "Missing database name."
    exit 1
fi

echo "Creating necessary tables..."
for ddl in "tweet" "created_tweet" "model"; do
    psql -h ${1} -U ${2} ${3} -a -f ./utils/sql/${ddl}.ddl.sql 
done
echo "Done."
