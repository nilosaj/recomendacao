setup :
	docker-compose  build

run :
	docker-compose  up

test:
	docker-compose exec principal python test_app.py