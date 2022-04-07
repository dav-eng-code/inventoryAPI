import sys
from datetime import datetime
from flask import Blueprint, request, abort, jsonify
from auth.auth import requires_auth
from models import Item, Container

containers_blueprint = Blueprint('containers_blueprint',__name__)

#as suggested in Udacity Review1 and based on https://realpython.com/flask-blueprint/

@containers_blueprint.route('/containers', methods=['GET'])
@requires_auth('get:containers')
def containers(payload):
    """This enpoint fetches details of the container with the given id or returns a 404 code if there is no match"""
    containers={c.id:c.name for c in Container.query.all()}
    response={
        'success':True,
        "Total Containers":len(Container.query.all()),
        "Containers List":containers
    }
    return jsonify(response)

@containers_blueprint.route('/containers/<string:name>', methods=['GET'])
@requires_auth('get:containers')
def containers_search_by_name(payload,name):
    """This enpoint fetches details of the named container or returns a 404 code if there is no match"""
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

@containers_blueprint.route('/containers/<int:id>', methods=['GET'])
@requires_auth('get:containers')
def containers_search_by_id(payload,id):
    """This enpoint fetches details of the container with the given id or returns a 404 code if there is no match"""
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

@containers_blueprint.route('/containers/add', methods=['POST'])
@requires_auth('post:containers')
def containers_add(payload):
    """This enpoint adds a new container with the given attributes"""
    try:
        data = request.get_json()
    except:
        print(sys.exc_info()) # added as per Udacity Review#1 suggestion
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
        print(sys.exc_info())
        abort(422)
    response={
        'success':True,
        'Total Containers':len(Container.query.all())
        }
    return response

@containers_blueprint.route('/containers/update', methods=['PATCH'])
@requires_auth('patch:containers')
def container_update(payload):
    """This enpoint updates container with the given details or returns 404 error if no matching id; requires the name and returns 409 error if the name does not match for the given id; if location is stated, all contained items will also have their location updated"""
    try:
        data = request.get_json()
    except:
        print(sys.exc_info())
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
        for item in container.items:
            item.location=container.location
    if 'container_value' in data:
        container.container_value=data['container_value']
        container.total_value=int(container.container_value)+int(container.contents_value)
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

@containers_blueprint.route('/containers/<int:id>', methods=['DELETE'])
@requires_auth('delete:containers')
def containers_delete_by_id(payload,id):
    """This enpoint deletes the specified container"""
    container=Container.query.filter(Container.id==id).one_or_none()
    if container == None:
        abort(404)
    container.delete()
    response={
        'success':True
    }
    return response

@containers_blueprint.route('/containers/search', methods=['POST'])
@requires_auth('get:containers')
def containers_search(payload):
    """This enpoint returns containers containing the given search term or 404 error if nothing matches"""
    try:
        data=request.get_json()
        search_term=data['search_term'].lower()
    except:
        print(sys.exc_info())
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