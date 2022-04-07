from datetime import datetime
from os import environ
import sys
from flask import Flask, redirect, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth.auth import AuthError, requires_auth
from models import db, Item, Container
from items_blueprint import items_blueprint
from containers_blueprint import containers_blueprint

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  app.register_blueprint(items_blueprint)
  app.register_blueprint(containers_blueprint)
  #CORS(app)

  DATABASE_URL=environ['DATABASE_URL'].replace('postgres://','postgresql://',1)
  
  app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  #db = SQLAlchemy(app)  #already created in the models file for use there, and imported along with the models
  db.app = app
  db.init_app(app)
  db.create_all()

  DOMAIN=environ['DOMAIN']
  API_IDENTIFIER=environ['API_AUDIENCE']
  CLIENT_ID=environ['CLIENT_ID']
  CALLBACK_URL=environ['CALLBACK_URL']
  
  login_address=f'https://{DOMAIN}/authorize?'\
                f'audience={API_IDENTIFIER}&'\
                f'response_type=token&'\
                f'client_id={CLIENT_ID}&'\
                f'redirect_uri={CALLBACK_URL}'
  
  logout_address=f'https://{DOMAIN}/v2/logout?'\
                f'client_id={CLIENT_ID}&'\
                f'returnTo={CALLBACK_URL}/login'

  @app.route('/login')
  def login():
    return f'<a href="{login_address}">Login here</a><br>'\
            f'<a href="{logout_address}">Logout here</a>'

  @app.route('/')
  def home_page():
    response={
      "Total Items": len(Item.query.all()),
      "Total Containers":len(Container.query.all())
    }
    return jsonify(response)

  @app.errorhandler(404)
  def error_not_found(error):
    data={
        'success':False,
        'error':error.code,
        'message':'The thing which it is that you are looking'\
                ' for has not been found. All search parties'\
                ' have returned.'
    }
    return jsonify(data),error.code

  @app.errorhandler(409)
  def error_conflict(error):
    data={
        'success':False,
        'error':error.code,
        'message':'Either the identification of the item you seek to update'\
                ' conflicts with the name you purport it to have,'\
                ' or you are providing a duplicate value.'\
                ' Please review and amend your request.'
    }
    return jsonify(data),error.code

  @app.errorhandler(422)
  def error_unprocessable(error):
    data={
        'success':False,
        'error':error.code,
        'message':'The thing which it is that are you trying to add'\
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