#!/bin/bash
set -eu
# Build Docker Containers
docker-compose up -d
# Pass The Reconstruction SQL To mysql And Run This In The DB Container
docker exec -it mysql_container bash -c 'mysql -u root -p${MYSQL_ROOT_PASSWORD} < /data/reconstruct.sql'
# Run Our App
python3 -m src.app