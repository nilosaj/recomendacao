from flask import Flask
from flask_restplus import Resource, Api
from flask_api import status
import json, logging
import DatabaseUtils

app_desafio = Flask(__name__)
api = Api(app_desafio)
parser = api.parser()
parser.add_argument('user', type=str, help='Usuario a ser utilizado no cadastro da visualizacao', location='form')

logging.basicConfig(level=logging.INFO)


@api.route('/<path:article>/view/')
class Document(Resource):
    @api.expect(parser)
    def post(self, article):
        args = parser.parse_args()
        if args["user"] is None:
            return None, status.HTTP_400_BAD_REQUEST
        else:
            resp = DatabaseUtils.register_view(args["user"], article)
            if len(resp) > 0:
                logging.debug("view [ {} ] : {}".format(article, resp))
                return None, status.HTTP_201_CREATED
            else:
                logging.debug("view [ {} ] : {}".format(article, resp))
                return None, status.HTTP_200_OK


@api.route('/<path:article>/similar/')
class Similarity(Resource):
    def get(self, article):
        resp = DatabaseUtils.get_similars(article)
        logging.debug(type(resp))
        if len(resp) > 0:
            return resp, status.HTTP_200_OK
        else:
            return None, status.HTTP_204_NO_CONTENT


@api.route('/')
class Persistence(Resource):
    def delete(self):
        resp = DatabaseUtils.clear_database()
        if resp:
            return resp, status.HTTP_200_OK
        else:
            return None, status.HTTP_500_INTERNAL_SERVER_ERROR




if __name__ == '__main__':
    app_desafio.run(debug=True, host='0.0.0.0',port=8080)
