docker-compose down -v && docker-compose up --abort-on-container-exit --remove-orphans &
sleep 4
cd concord && poetry run python -m pytest --pdb && cd .. || cd ..
docker-compose down -v