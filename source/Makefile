run:
	@docker-compose up -d --build

debug:
	@docker-compose up --build

stop:
	@docker-compose down

clean:
	@docker-compose down
	@docker system prune -f
	@docker volume prune -f
	@docker network prune -f
	@docker image prune -f
	@docker container prune -f

restart: stop debug

cleandb:
	@docker volume rm $(shell docker volume ls -q)

fclean: clean
	@rm -rf bob/ourapp/__pycache__
	@rm -rf bob/ourapp/migrations
	@rm -rf bob/ourapp/static
	@rm -rf bob/oursolution/__pycache__
	@docker rmi -f $(shell docker images -q)
	@docker volume rm $(shell docker volume ls -q)
