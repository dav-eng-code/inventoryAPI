import sys
from datetime import datetime
from flask import Blueprint, request, abort, jsonify
from auth.auth import requires_auth
from models import Item, Container

items_blueprint = Blueprint('items_blueprint',__name__)

#as suggested in Udacity Review1 and based on https://realpython.com/flask-blueprint/

@items_blueprint.route('/items', methods=['GET'])
@requires_auth('get:items')
def items(payload):
    """fetches a list of the items in key-value pairs with the format id:name"""
    items={c.id:c.name for c in Item.query.all()}
    response={
        'success':True,
        "Total Items":len(Item.query.all()),
        "Items List":items
    }
    return jsonify(response)

@items_blueprint.route('/items/<string:name>', methods=['GET'])
@requires_auth('get:items')
def items_search_by_name(payload,name):
    """fetches details of the named item or returns a 404 code if there is no match"""
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

@items_blueprint.route('/items/<int:id>', methods=['GET'])
@requires_auth('get:items')
def items_search_by_id(payload,id):
    """fetches details of the item with the given id or returns a 404 code if there is no match"""
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

@items_blueprint.route('/items/add', methods=['POST'])
@requires_auth('post:items')
def items_add(payload):
    """adds item with the given details"""
    try:
        data = request.get_json()
    except:
        print(sys.exc_info())
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
        print(sys.exc_info())
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
        container.contents_value=int(container.contents_value)+int(item.value)
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

@items_blueprint.route('/items/update', methods=['PATCH'])
@requires_auth('patch:items')
def item_update(payload):
    """updates item with the given details and updates its container or returns 404 error if no matching id; requires the name and returns 409 error if the name does not match for the given id; returns 409 error if location is stated but does not match the container location"""
    try:
        data = request.get_json()
    except:
        print(sys.exc_info())
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
        if item.container_id!=None and Container.query.get(item.container_id).location!=data['location']:
            abort(409)
        item.location=data['location']
    original_value=0
    if 'value' in data:
        original_value=item.value
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
        else:
            item.location=container.location
            item.container_id=data['container_id']
            container.contents_value=int(container.contents_value)-int(original_value)+int(item.value)
            container.total_value=int(container.container_value)+int(container.contents_value)
            container.date_updated=datetime.utcnow()
    try:
        item.update()
    except:
        print(sys.exc_info())
        abort(422)
    response={
        'success':True,
        'Total Items':len(Item.query.all()),
        'container':item.container_id
        }
    return response

@items_blueprint.route('/items/<int:id>', methods=['DELETE'])
@requires_auth('delete:items')
def items_delete_by_id(payload,id):
    """deletes the specified item"""
    item=Item.query.filter(Item.id==id).one_or_none()
    if item == None:
        abort(404)
    item.delete()
    response={
        'success':True
    }
    return response

@items_blueprint.route('/items/search', methods=['POST'])
@requires_auth('get:items')
def items_search(payload):
    """returns items containing the given search term or 404 error if nothing matches"""
    try:
        data=request.get_json()
        search_term=data['search_term'].lower()
    except:
        print(sys.exc_info())
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