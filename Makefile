#Makefile

up:
	cp env/.env.prod .env
	docker-compose up

build:
	cp env/.env.prod .env
	docker-compose up --build

test:
	trap 'docker-compose down && exit 0' INT;
	cp env/.env.test .env
	docker-compose --file dev.yml up
	docker-compose down

lint:
	autopep8 --in-place --recursive .

