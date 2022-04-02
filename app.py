#import os
from flask import Flask, redirect, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth.auth import AuthError, requires_auth
from models import db, Item, Container


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  CORS(app)

  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp_sqlite_db/main.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  #db = SQLAlchemy(app)  #already created in the models file for use there, and imported along with the models
  db.app = app
  db.init_app(app)
  db.create_all()


  @app.route('/login')
  def login():
    DOMAIN='dav-eng-code-testing.eu.auth0.com'
    API_IDENTIFIER='https://productivity-inventory.herokuapp.com/'
    CLIENT_ID='Q7pQU8jGRAiOCGEqn55STzPPmevq3rsb'
    CALLBACK_URL='http://localhost:5000'
    address=f'https://{DOMAIN}/authorize?'\
            f'audience={API_IDENTIFIER}&'\
            f'response_type=token&'\
            f'client_id={CLIENT_ID}&'\
            f'redirect_uri={CALLBACK_URL}'
    return f'<a href="{address}">Login here</a>'


  @app.route('/')
  def home_page():
    response={
      "Total Items": len(Item.query.all()),
      "Total Containers":len(Container.query.all())
    }
    return jsonify(response)

  @app.route('/containers', methods=['GET'])
  @requires_auth('get:containers')
  def containers(payload):

    containers={c.id:c.name for c in Container.query.all()}
    response={
      'success':True,
      "Total Containers":len(Container.query.all()),
      "Containers List":containers
    }
    return jsonify(response)

  @app.route('/containers/<string:name>', methods=['GET'])
  def containers_search_by_name(name):
    container=Container.query.filter(Container.name==name).one_or_none()
    if container == None:
      abort(404)
    response={
      'success':True,
      'id':container.id,
      'name':container.name,
      'location':container.location,
      'container_value':container.container_value
    }
    return response

  @app.route('/containers/<int:id>', methods=['GET'])
  def containers_search_by_id(id):
    container=Container.query.filter(Container.id==id).one_or_none()
    if container == None:
      abort(404)
    response={
      'success':True,
      'id':container.id,
      'name':container.name,
      'location':container.location,
      'container_value':container.container_value
    }
    return response

  @app.route('/containers/add', methods=['POST'])
  def containers_add():
    data = request.get_json()
    if data==None:
      abort(422)
    container = Container(
      name=data['name'],
      location=data['location'],
      container_value=data['container_value']
      )
    container.insert()
    response={
      'success':True,
      'Total Containers':len(Container.query.all())
      }

    return response

  @app.errorhandler(404)
  def not_found(error):
    data={
      'success':False,
      'error':error.code,
      'message':'The thing which it is that you are looking'\
                ' for has not been found. All search parties'\
                ' have returned.'
    }
    return jsonify(data),error.code

  @app.errorhandler(422)
  def not_found(error):
    data={
      'success':False,
      'error':error.code,
      'message':'The thing which it is that are trying to add'\
                ' you have not availed of the appropriate data'\
                ' that is required for the thing you desire to add.'
    }
    return jsonify(data),error.code




  #errorhandler source https://auth0.com/docs/quickstart/backend/python
  @app.errorhandler(AuthError)
  def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


  return app



APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)