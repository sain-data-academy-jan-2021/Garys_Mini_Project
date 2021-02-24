#!/bin/bash
set -eu
docker-compose up -d
docker exec -it mysql_container bash -c 'mysql -u root -p${MYSQL_ROOT_PASSWORD} < /data/reconstruct.sql'
python3 -m src.app