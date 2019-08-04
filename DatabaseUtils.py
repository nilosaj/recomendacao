import RedisConnector


dbConn = RedisConnector.connectRedis()


def register_view(user, article):
    """
    Funcao responsavel por persistir dados da visualizacao feita pelo usuario
    :param user: usuario que visualizou o artigo
    :param article:  artigo visualizado pelo usuario
    :return: informacoes referentes a criação ou não de novos registros na base  , para fins de log
    """
    resp = {}
    if not(dbConn.sismember("users", user)):     # criacao do Redis SET de usuarios
        dbConn.sadd("users", user)
        resp["user"] = True
    if not(dbConn.sismember("articles", article)): # criacao do Redis SET de artigos
        dbConn.sadd("articles", article)
        resp["document"] = True
    if not(dbConn.sismember("user:"+user, article)):  # criacao do Redis SET de artigos visualizados por cada usuario
        dbConn.sadd("user_article:"+user, article)
        resp["user_article"] = True
    if not(dbConn.sismember("article:"+article, user)): # criacao do Redis SET de usuarios que visualizaram cada arquivo
        dbConn.sadd("article:"+article, user)
        resp["article_view"] = True
    return resp


def get_similars(article):
    """
    Funcao responsavel por recuperar artigos similares ao artigo da busca
    :param article: artigo o qual serao buscados arrtigos similares
    :return: lista de tuplas contendo artigos similares e seus scores
    """
    candidates = set()
    users_viewed_article = dbConn.smembers("article:"+article) #recupera usuarios que ja viram este artigo
    # recupera  lista de artigos visualizados pelos usuarios que ja acessaram o artigo original
    for user in users_viewed_article:
        for varticle in dbConn.smembers("user_article:"+user):
            if varticle != article:
                candidates.add(varticle)

    return calcJaccard(users_viewed_article, candidates)



def clear_database():
    return dbConn.flushdb()


def calcJaccard(users_original_article,candidate_articles):
    """
    funcao responsavel pelo calculo da distancia jaccard
    :param users_original_article:  set de usuarios associados ao artigo orignal da busca
    :param candidate_articles:  set de artigos que possuem visualizacao por parte dos usuarios que visualizaram o artigo original da busca
    :return: lista de tuplas  contendo o score da distancia jaccard ordenados de forma descendente
    """
    resp = {}
    for varticle in candidate_articles:
        varticle_users = dbConn.smembers("article:"+ varticle)
        resp[varticle] = len(users_original_article.intersection(varticle_users))/(len(users_original_article.union(varticle_users)))
    return sorted(resp.items(), key=lambda x: x[1], reverse=True)

