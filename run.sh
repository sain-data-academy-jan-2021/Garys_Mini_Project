docker-compose up -d
#docker exec -it mysql_container mysql -u root -p${MYSQL_ROOT_PASSWORD} < /data/reconstruct.sql
docker exec -it mysql_container sh /data/reconstruct.sh
docker exec -it mini_project_app_container python3 -m src.app
