from app import app_desafio
import logging, json
import unittest


class TestView(unittest.TestCase):

    logging.basicConfig(level=logging.INFO)

    def setUp(self):
        self.app = app_desafio.test_client()
        # prepara a base para teste
        self.app.delete("/")
        self.app.post('/1/view/', data="user=A", content_type='application/x-www-form-urlencoded')
        self.app.post('/2/view/', data="user=A", content_type='application/x-www-form-urlencoded')
        self.app.post('/3/view/', data="user=A", content_type='application/x-www-form-urlencoded')
        self.app.post('/1/view/', data="user=B", content_type='application/x-www-form-urlencoded')
        self.app.post('/2/view/', data="user=B", content_type='application/x-www-form-urlencoded')
        self.app.post('/5/view/', data="user=B", content_type='application/x-www-form-urlencoded')
        self.app.post('/1/view/', data="user=C", content_type='application/x-www-form-urlencoded')
        self.app.post('/2/view/', data="user=C", content_type='application/x-www-form-urlencoded')
        self.app.post('/4/view/', data="user=C", content_type='application/x-www-form-urlencoded')


    def test_clear_database(self):
        """
        Teste referente a interface de limpeza da base de dados
        """
        logging.info("Teste de cleanup da base")
        resp = self.app.delete("/")
        self.assertEqual(resp.status_code, 200)

    def test_register_view_new_user(self):
        """
        Teste referente a interface de criação de novas visualizacoes para novos usuários
        """
        logging.info("Teste de cadastro de  visualizacao por novo usuario")
        resp = self.app.post('/98/view/', data="user=Z", content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, 201)

    def test_register_view_exist_user(self):
        """
        Teste referente a interface de criação de novas visualizacoes para usuario pre existente
        """
        logging.info("Teste de cadastro de  visualizacao por usuario existente na base")
        resp = self.app.post('/97/view/', data="user=Z", content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, 201)

    def test_repeat_register_view(self):
        """
        Teste referente a tentativa de recriar uma visualizacao
        """
        logging.info("Teste de repeticao de cadastro de  visualizacao")
        resp = self.app.post('/2/view/', data="user=A", content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, 200)

    def test_similar_view(self):
        logging.info("Teste de retorno de consulta de similaridade ")
        expected_data = [{"url": "2", "score": 1.0}, {"url": "5", "score": 0.3333333333333333},{"url": "4", "score": 0.3333333333333333}, {"url": "3", "score": 0.3333333333333333}]
        resp = self.app.get('/1/similar/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data(as_text=True).replace("\n", ''), json.dumps(expected_data).replace("'", '"'))

    def test_not_exist_similar_view(self):
        """
        Teste referente a tentativa de recuperar  uma pagina similar  a um documento nao existente na base
        """
        logging.info("Teste de ausencia de  similaridade por pagina inexistente na base")
        resp = self.app.get('/99/similar/')
        self.assertEqual(resp.status_code, 204)

    def test_similarity_change_score(self):
        """
        Teste referente a mudanca no score de similaridade de um documento devido a visualizacao do mesmo por um outro usuario
        """
        logging.info("Teste de mudanca de  score de similaridade devido a nova visualizacao em pagina similar ")
        expected_data = [{"url": "2", "score": 1.0}, {"url": "5", "score": 0.3333333333333333},{"url": "4", "score": 0.3333333333333333}, {"url": "3", "score": 0.3333333333333333}]
        resp = self.app.get('/1/similar/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data(as_text=True).replace("\n", ''), json.dumps(expected_data).replace("'", '"'))
        resp = self.app.post('/2/view/', data="user=D", content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, 201)
        resp = self.app.get('/1/similar/')
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.get_data(as_text=True).replace("\n", ''), json.dumps(expected_data).replace("'", '"'))
        expected_data = [{"url": "2", "score": 0.75}, {"url": "5", "score": 0.3333333333333333},{"url": "4", "score": 0.3333333333333333}, {"url": "3", "score": 0.3333333333333333}]
        self.assertEqual(resp.get_data(as_text=True).replace("\n", ''), json.dumps(expected_data).replace("'", '"'))

    def test_similarity_new_similar(self):
        """
        Teste referente a mudanca na lista de similaridades devido a visualizacao de  um novo documento por parte de um usuario que visualizou documento da busca
        """
        logging.info("Teste de inclusao de visualizacao de novo documento por usuario que visualizou documento da busca")
        expected_data = [{"url": "2", "score": 1.0}, {"url": "5", "score": 0.3333333333333333},{"url": "4", "score": 0.3333333333333333}, {"url": "3", "score": 0.3333333333333333}]
        resp = self.app.get('/1/similar/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data(as_text=True).replace("\n", ''), json.dumps(expected_data).replace("'", '"'))
        resp = self.app.post('/9/view/', data="user=A", content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, 201)
        resp = self.app.get('/1/similar/')
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.get_data(as_text=True).replace("\n", ''), json.dumps(expected_data).replace("'", '"'))
        expected_data = [{"url": "2", "score": 1.0}, {"url": "9", "score": 0.3333333333333333}, {"url": "5", "score": 0.3333333333333333},{"url": "4", "score": 0.3333333333333333}, {"url": "3", "score": 0.3333333333333333}]
        self.assertEqual(resp.get_data(as_text=True).replace("\n", ''), json.dumps(expected_data).replace("'", '"'))


if __name__ == '__main__':
    unittest.main()