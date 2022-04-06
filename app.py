from datetime import datetime
from os import environ
from flask import Flask, redirect, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth.auth import AuthError, requires_auth
from models import db, Item, Container


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  CORS(app)

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

  @app.route('/containers', methods=['GET'])
  #@requires_auth('get:containers')
  def containers(*args):

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
      'container_value':container.container_value,
      'total_value':container.total_value,
      'items':[item.name for item in container.items]
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
      'container_value':container.container_value,
      'total_value':container.total_value,
      'items':[item.name for item in container.items]
    }
    return response

  @app.route('/containers/add', methods=['POST'])
  def containers_add():
    try:
      data = request.get_json()
    except:
      abort(422)
    c = Container.query.filter(Container.name==data['name']).one_or_none()
    if c!=None:
      abort(409)
    try:
      container = Container(
        name=data['name'],
        location=data['location'],
        container_value=data['container_value']
        )
      container.insert()
    except:
      abort(422)
    response={
      'success':True,
      'Total Containers':len(Container.query.all())
      }
    return response

  @app.route('/containers/update', methods=['PATCH'])
  def container_update():
    try:
      data = request.get_json()
    except:
      abort(422)
    id=data['id']
    container = Container.query.filter(Container.id==id).one_or_none()
    if container==None:
      abort(404)
    if data['name']!=container.name:
      abort(409)
    # for attribute in ['name','location','container_value']:
    #   if attribute in data:
    #     container[attribute]=data[attribute]
    if 'location' in data:
      container.location=data['location']
    if 'container_value' in data:
      container.container_value=data['container_value']
    container.update()
    response={
      'success':True,
      'id':container.id,
      'name':container.name,
      'location':container.location,
      'container_value':container.container_value,
      'total_value':container.total_value,
      'items':[item.name for item in container.items]
      }
    return response

  @app.route('/containers/<int:id>', methods=['DELETE'])
  def containers_delete_by_id(id):
    container=Container.query.filter(Container.id==id).one_or_none()
    if container == None:
      abort(404)
    container.delete()
    response={
      'success':True
    }
    return response

  @app.route('/containers/search', methods=['POST'])
  def containers_search():
    try:
      data=request.get_json()
      search_term=data['search_term'].lower()
    except:
      abort(422)
    c=Container.query.filter(Container.name.ilike('%'+search_term+'%')).all()
    if c == []:
      abort(404)
    containers=[]
    for container in c:
      containers.append({
        'id':container.id,
        'name':container.name,
        'location':container.location,
        'container_value':container.container_value,
        'total_value':container.total_value,
        'items':[item.name for item in container.items]
      })
    response={
      'success':True,
      'results':containers
    }
    return response

  @app.route('/items', methods=['GET'])
  def items(*args):

    items={c.id:c.name for c in Item.query.all()}
    response={
      'success':True,
      "Total Items":len(Item.query.all()),
      "Items List":items
    }
    return jsonify(response)

  @app.route('/items/<string:name>', methods=['GET'])
  def items_search_by_name(name):
    item=Item.query.filter(Item.name==name).one_or_none()
    if item == None:
      abort(404)
    response={
      'success':True,
      'id':item.id,
      'name':item.name,
      'location':item.location,
      'value':item.value
    }
    return response

  @app.route('/items/<int:id>', methods=['GET'])
  def items_search_by_id(id):
    item=Item.query.filter(Item.id==id).one_or_none()
    if item == None:
      abort(404)
    response={
      'success':True,
      'id':item.id,
      'name':item.name,
      'location':item.location,
      'value':item.value
    }
    return response

  @app.route('/items/add', methods=['POST'])
  def items_add():
    try:
      data = request.get_json()
    except:
      abort(422)
    i = Item.query.filter(Item.name==data['name']).one_or_none()
    if i!=None:
      abort(409)
    try:
      item = Item(
        name=data['name'],
        location=data['location'],
        value=data['value'],
        status=data['status']
        )
    except:
      abort(422)
    if 'tag' in data:
      item.tag=data['tag']
    if 'location' in data:
      item.location=data['location']
    if 'value' in data:
      item.value=data['value']
    if 'status' in data:
      item.status=data['status']
    if 'date_updated' in data:
      item.date_updated=data['date_updated']
    if 'container' in data:
      container=Container.query.get(data['container'])
      if container==None:
        abort(409)
      if data['location']!=container.location:
        abort(409)
      container.value=container.value+item.value
      container.date_updated=datetime.utcnow()
    try:
      item.insert()
    except:
      abort(422)
    response={
      'success':True,
      'Total Items':len(Item.query.all())
      }
    return response

  @app.route('/items/update', methods=['PATCH'])
  def item_update():
    try:
      data = request.get_json()
    except:
      abort(422)
    if 'name' not in data or 'id' not in data:
      abort(422)
    id=data['id']
    item = Item.query.filter(Item.id==id).one_or_none()
    if item==None:
      abort(404)
    if data['name']!=item.name:
      abort(409)
    if 'tag' in data:
      item.tag=data['tag']
    if 'location' in data:
      item.location=data['location']
    if 'value' in data:
      item.value=data['value']
    if 'status' in data:
      item.status=data['status']
    if 'date_updated' in data:
      item.date_updated=datetime.strptime(data['date_updated'],'%Y-%m-%d %H:%M:%S')
    if 'container_id' in data:
      container=Container.query.get(data['container_id'])
      if container==None:
        abort(409)
      if 'location' in data and data['location']!=container.location:
        abort(409)
      item.container_id=data['container_id']
      container.contents_value=int(container.contents_value)+int(item.value)
      container.total_value=int(container.container_value)+int(container.contents_value)
      container.date_updated=datetime.utcnow()
    try:
      item.update()
    except:
      abort(422)
    response={
      'success':True,
      'Total Items':len(Item.query.all()),
      'container':item.container_id
      }
    return response

  @app.route('/items/<int:id>', methods=['DELETE'])
  def items_delete_by_id(id):
    item=Item.query.filter(Item.id==id).one_or_none()
    if item == None:
      abort(404)
    item.delete()
    response={
      'success':True
    }
    return response

  @app.route('/items/search', methods=['POST'])
  def items_search():
    try:
      data=request.get_json()
      search_term=data['search_term'].lower()
    except:
      abort(422)
    i=Item.query.filter(Item.name.ilike('%'+search_term+'%')).all()
    if i == []:
      abort(404)
    items=[]
    for item in i:
      items.append({
        'id':item.id,
        'name':item.name,
        'location':item.location,
        'value':item.value
      })
    response={
      'success':True,
      'results':items
    }
    return response


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