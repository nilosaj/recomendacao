# Desafio Big Data: Sistema de Recomendação - Solução



# Desafio:
- Recomendar documentos similares a um outro no estilo  ["quem viu isso, também viu..."](https://en.wikipedia.org/wiki/Collaborative_filtering).

> Exemplo: se o usuário  A  viu os documentos 1, 2 e 3; o  B  viu 1, 2 e 5; e o  C  viu 1, 2 e 4, a API deve dizer que o documento 1 é similar ao 2.

- A escolha do algoritmo de similaridade é livre (ex: distância de Jaccard)
- A solução deverá estar encapsulada em container(s) Docker
- Criação de interface POST `/<url>/view`  utilizada para registrar uma visualização de um usuário a uma página
- Criação de interface GET `/<url>/similar` utilizada para recuperar páginas similares a página buscada 
- Criação de interface DELETE `/`utilizada para remover todos os registros da base de dados
- *Build* do container principal via `make setup`
- *Start* da solução via `make run`

> **obs:** A estrutura de retorno das interfaces também  é descrita  no documento do desafio.

# Proposta:
- Uma vez que a principal regra de arquitetura da solução é o encapsulamento em  container(s)  docker   fica em aberto a  escolha da linguagem utilizada  . As opções são diversas tais como Nodejs+Express , Java + Spring Boot , Python + Flask  e etc. Para solução foi escolhida Python + Flask simplesmente pela grande aceitação da linguagem no contexto de soluções Big Data . 
- Para o algoritmo de similaridade foi escolhida a Distância de Jaccard a ser implementada  sem a utilização de bibliotecas especificas  para solução de problemas de similaridade.
- Para persistência de dados  será utilizado Redis pela simplicidade da tecnologia , pelo excelente tempo de resposta da consulta e finalmente pela estrutura de SET e suas funções que serão utilizados na solução.  
- Não serão considerados os tokens contidos no conteúdo de cada página , isto é , a similaridade não será calculada com base nos termos contidos no texto ou por semântica.




##  Interface `/<url>/view` 
A interface de registro de visualizações tem como payload do request a informação do usuário da seguinte forma:
`user=user1`
o Parser deverá recuperar o dado do usuário e  juntamente com a informação da url persistir as informações de forma que facilite a verificação de similaridade em uma consulta via outra interface. na solução proposta a interface  persiste  as seguintes  informações no Redis:
- SET  cuja  chave é `"users"`  no qual é armazenado o usuário informado . este usuário já pode estar contido no conjunto de usuários deste SET devido a visualizações anteriores a mesma url ou a outras urls. 
- SET cuja chave é `"articles"` no qual é armazenada a url consultada. esta url já pode estar contida no conjunto de urls deste SET devido a visualizações anteriores pelo usuário corrente ou por outros usuários.
- SET cuja chave é `"user_article:<user>"` no qual é armazenado o conjunto de paginas visualizadas por um usuário especifico.esta url já pode estar contida no conjunto de urls deste SET devido a visualizações anteriores pelo usuário corrente.
- SET cuja chave é `"article:<url>"` no qual é armazenado o conjunto de usuários que visualizaram uma pagina especifica. este usuário já pode estar contido no conjunto de usuários deste SET devido a visualizações anteriores a mesma url .
Efetivamente para  verificação de similaridade serão utilizados os SETS `"user_article:<user>"`  e `"article:<url>"`

## Interface `/<url>/similar`

A Interface de recuperação de artigos similares recupera a URL do path , que é a pagina da consulta de similaridade ,  e  efetua  as seguintes  ações:
1. Recupera a lista de usuários que já acessaram esta URL  a partir do SET `"article:<url>"`
2. Para cada usuário descrito no passo anterior recupera através do SET `"user_article:<user>"` todas as paginas visualizadas por este usuário excetuando a pagina da consulta . todas estas paginas são considerados candidatos a serem paginas similares e  armazenados.
3. Para cada página candidata será calculada a distância Jaccard em relação a pagina da consulta considerando os usuários que acessaram estas paginas , isto é:
	Seja A o conjunto de usuários que acessou a página  da consulta
	Seja B o conjunto de usuários que acessou a pagina candidata corrente
	`Jaccard = tamanho(A.intersect(B)) / tamanho(A.union(B)) `
4. Após o calculo da distância de todas  as paginas candidatas em relação à pagina da consulta  serão retornadas as  10 primeiras em ordem decrescente de score

Utilizando o exemplo descrito no documento de desafio:

> se o usuário  A  viu os documentos 1, 2 e 3; o  B  viu 1, 2 e 5; e o  C  viu 1, 2 e 4, a API deve dizer que o documento 1 é similar ao 2.

O estado da base de dados após todas as views cadastradas seria :

    - [SET]  articles   ->  [1,2,3,4,5]
    - [SET]  users -> [A, B , C]
    - [SET]  article:1 -> [A,B,C]
    - [SET]  article:2 -> [A,B,C]
    - [SET]  article:3 -> [A]
    - [SET]  article:4 -> [B]
    - [SET]  article:5 -> [C]
    - [SET]  user:A -> [1,2,3]
    - [SET]  user:B -> [1,2,5]
    - [SET]  user:C -> [1,2,3]

A consulta por documentos similares ao documento 1 se daria da seguinte forma:

1. recuperar usuários que consultaram o documento 1  , ou seja , `[SET]  article:1 -> [A,B,C]`
2. para cada usuário recuperar os artigos lidos , ou seja :
	- [SET]  user:A -> [1,2,3]
	- [SET]  user:B -> [1,2,5]
	- [SET]  user:C -> [1,2,3]
	
    que correspondem ao domínio de paginas 1,2,3,4,5  . remove-se a pagina da consulta , isto é pagina 1 , e o dominio final é 2,3,4,5 e  estas são as páginas candidatas.

3. para cada página candidata recuperar  seu conjunto de usuários e calcular a distância Jaccard :

    ***Artigo 1 (pesquisa) x Artigo 2 (candidato)***
    
            - Artigo 1	[SET]  article:2 -> [A,B,C]
            - Artigo 2	[SET]  article:2 -> [A,B,C]
            - Jaccard (Artigo1,Artigo2)  =  (A,B,C).intersect(A,B,C)/ (A,B,C).union(A,B,C) 
            - Jaccard (Artigo1,Artigo2)= 1.0
    
    ***Artigo 1(pesquisa) x Artigo 3(candidato)***

            - Artigo 1	[SET]  article:2 -> [A,B,C]
            - Artigo 3	[SET]  article:2 -> [A]
            - Jaccard (Artigo1,Artigo3)  =  (A,B,C).intersect(A)/ (A,B,C).union(A) 
            - Jaccard (Artigo1,Artigo3)= 0.333333


