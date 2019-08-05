setup :
	@echo "Efetuando build da(s) imagem(ns) docker."
	docker-compose  build

run :
	@echo "Inicializando aplicação."
	docker-compose  up

test:
	@echo "Executando testes da aplicação."
	docker-compose exec desafio python test_app.py