from datetime import datetime
import unittest
import json
from os import environ
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import db, Container, Item


class TestInventoryApp(unittest.TestCase):

    #setup the app for testing
    def setUp(self):
        self.app = create_app()
        self.app.testing=True
        self.client=self.app.test_client()
        
        DATABASE_URL=environ['DATABASE_URL'].replace('postgres://','postgresql://',1)
  
        self.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.app = self.app
        db.init_app(self.app)
        db.drop_all()
        db.create_all()
        

    #execute this function are every test
    def tearDown(self):
        db.drop_all()
        db.create_all()
        # c=Container.query.filter(Container.name=='myNewContainer').one_or_none()        
        # if not c == None:
        #     c.delete()
        # c=Container.query.filter(Container.name=='shortlivedcontainer').one_or_none()        
        # if not c == None:
        #     c.delete()
        # c=Container.query.filter(Container.id==4321).one_or_none()        
        # if not c == None:
        #     c.delete()

        # c=Item.query.filter(Item.name=='myNewItem').one_or_none()        
        # if not c == None:
        #     c.delete()
        # c=Item.query.filter(Item.name=='shortliveditem').one_or_none()        
        # if not c == None:
        #     c.delete()
        # c=Item.query.filter(Item.id==4321).one_or_none()        
        # if not c == None:
        #     c.delete()

    #test the root endpoint, GET /
    def test_homepage(self):
        result=self.client.get('/')
        data=json.loads(result.data)
        self.assertGreaterEqual(data['Total Items'],0)
        self.assertGreaterEqual(data['Total Containers'],0)


    #CONTAINERS
    
    #prep functions for use in tests
    def prep_insert_container(self,name):
        container = Container(
        name=name,
        location='over_there',
        container_value=3000
        )
        container.insert()

    def prep_remove_container(self):
        c=Container.query.filter(Container.name=='shortlivedcontainer').one_or_none()        
        if not c == None:
            c.delete()

    #GET containers/
    def test_get_containers(self):
        #need to include authorization header in request
        token=environ['ADMIN_TOKEN']

        #repeat with different role tokens
        #check that it fails both with wrong role and without any token
        result=self.client.get('/containers', headers={'Authorization':'Bearer '+token})
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['Total Containers'],0)
        self.assertIsNotNone(data['Containers List'])

    #GET containers/<string:name>
    def test_get_container_by_name(self):
        #for token in [environ['ADMIN_TOKEN'],environ['MOVER_TOKEN'],environ['ORGANISER_TOKEN'],environ['DOCUMENTER_TOKEN']]:
            self.prep_insert_container('shortlivedcontainer')
            result=self.client.get('/containers/shortlivedcontainer')#, headers={'Authorization':'Bearer '+token})
            data=json.loads(result.data)
            self.assertEqual(result.status_code,200)
            self.assertTrue(data['success'])
            self.assertEqual(data['id'],1)
            self.assertEqual(data['name'],'shortlivedcontainer')
            self.assertEqual(data['location'],'over_there')
            self.assertEqual(data['container_value'],3000)
            self.assertIsNotNone(data['total_value'])
    
    def test_get_container_by_name_not_found(self):
        result=self.client.get('/containers/nonexistantcontainer')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    #GET containers/<int:id>
    def test_get_container_by_id(self):
        self.prep_insert_container('shortlivedcontainer')
        result=self.client.get('/containers/1')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['id'],1)
        self.assertEqual(data['name'],'shortlivedcontainer')
        self.assertEqual(data['location'],'over_there')
        self.assertEqual(data['container_value'],3000)
        self.assertIsNotNone(data['total_value'])

    def test_get_container_by_id_not_found(self):
        result=self.client.get('/containers/4321')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    #POST containers/add
    def test_add_container(self):
        result=self.client.post('/containers/add',
        json={
            'name':'myNewContainer',
            'location':'somewhere',
            'container_value':'0.55'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
    
    def test_add_container_duplicate_name(self):
        result=self.client.post('/containers/add',
        json={
            'name':'myNewContainer',
            'location':'somewhere',
            'container_value':'0.55'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        result=self.client.post('/containers/add',
        json={
            'name':'myNewContainer',
            'location':'anywhere',
            'container_value':777
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,409)
        self.assertFalse(data['success'])

    def test_add_container_unprocessable(self):
        result=self.client.post('/containers/add')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,422)
        self.assertFalse(data['success'])

    #POST containers/update
    def test_update_container(self):
        self.prep_insert_container('shortlivedcontainer')
        result=self.client.patch('/containers/update',
        json={
            'id':1,
            'name':'shortlivedcontainer',
            'container_value':777
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])

    def test_update_container_not_found(self):
        result=self.client.patch('/containers/update',
        json={
            'id':1,
            'name':'shortlivedcontainer',
            'container_value':777
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    def test_update_container_unprocessable(self):
        self.prep_insert_container('shortlivedcontainer')
        result=self.client.patch('/containers/update',
        json={
            'id':1,
            'name':'wrongName',
            'container_value':777
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,409)
        self.assertFalse(data['success'])
    
    #DELETE containers/<int:id>
    def test_delete_container(self):
        self.prep_insert_container('shortlivedcontainer')
        self.assertIsNotNone(Container.query.filter(Container.id==1).one_or_none())
        result=self.client.delete('/containers/1')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertIsNone(Container.query.filter(Container.id==1).one_or_none())

    def test_delete_container_not_found(self):
        result=self.client.delete('/containers/4321')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    #POST containers/search
    def test_container_search(self):
        self.prep_insert_container('shortlivedcontainer')
        result=self.client.post('/containers/search',
        json={
            'search_term':'Lived'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data,{
            'success':True,
            'id':1,
            'name':'shortlivedcontainer',
            'location':'over_there',
            'container_value':3000
            })

    def test_container_search_not_found(self):
        self.prep_insert_container('shortlivedcontainer')
        result=self.client.post('/containers/search',
        json={
            'search_term':'quack'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    #ITEMS

        
    #prep functions for use in tests
    def prep_insert_item(self,item_name):
        item = Item(
        name=item_name,
        location='over_here',
        value=3000,
        status= 'ok'
        )
        item.insert()

    def prep_remove_item(self,item_name):
        c=Item.query.filter(Item.name==item_name).one_or_none()        
        if not c == None:
            c.delete()

    #GET items/
    def test_get_items(self):
        #need to include authorization header in request
        token=environ['ADMIN_TOKEN']

        #repeat with different role tokens
        #check that it fails both with wrong role and without any token
        result=self.client.get('/items', headers={'Authorization':'Bearer '+token})
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['Total Items'],0)
        self.assertIsNotNone(data['Items List'])

    #GET items/<string:name>
    def test_get_item_by_name(self):
        #for token in [environ['ADMIN_TOKEN'],environ['MOVER_TOKEN'],environ['ORGANISER_TOKEN'],environ['DOCUMENTER_TOKEN']]:
            self.prep_insert_item('shortliveditem')
            result=self.client.get('/items/shortliveditem')#, headers={'Authorization':'Bearer '+token})
            data=json.loads(result.data)
            self.assertEqual(result.status_code,200)
            self.assertTrue(data['success'])
            self.assertEqual(data['id'],1)
            self.assertEqual(data['name'],'shortliveditem')
            self.assertEqual(data['location'],'over_here')
            self.assertEqual(data['value'],3000)
    
    def test_get_item_by_name_not_found(self):
        result=self.client.get('/items/nonexistantitem')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    #GET items/<int:id>
    def test_get_item_by_id(self):
        self.prep_insert_item('shortliveditem')
        result=self.client.get('/items/1')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['id'],1)
        self.assertEqual(data['name'],'shortliveditem')
        self.assertEqual(data['location'],'over_here')
        self.assertEqual(data['value'],3000)

    def test_get_item_by_id_not_found(self):
        result=self.client.get('/items/4321')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    #POST items/add
    def test_add_item(self):
        result=self.client.post('/items/add',
        json={
            'name':'myNewItem',
            'location':'somewhere',
            'value':'0.56',
            'status':'ok'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])

    def test_add_item_duplicate_name(self):
        result=self.client.post('/items/add',
        json={
            'name':'myNewItem',
            'location':'somewhere',
            'value':'0.56',
            'status':'ok'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        result=self.client.post('/items/add',
        json={
            'name':'myNewItem',
            'location':'elsewhere',
            'value':56000,
            'status':'missing'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,409)
        self.assertFalse(data['success'])

    def test_add_item_unprocessable(self):
        result=self.client.post('/items/add')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,422)
        self.assertFalse(data['success'])

    #POST items/update
    def test_update_item(self):
        self.prep_insert_item('shortliveditem')
        result=self.client.patch('/items/update',
        json={
            'id':1,
            'name':'shortliveditem',
            'status':'borrowed for min',
            'date_updated':str(datetime(2022,4,1))
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])

    def test_update_item_not_found(self):
        result=self.client.patch('/items/update',
        json={
            'id':1,
            'name':'shortliveditem',
            'status':'borrowed for min',
            'date_updated':str(datetime(2022,4,1))
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    def test_update_item_unprocessable(self):
        self.prep_insert_item('shortliveditem')
        result=self.client.patch('/items/update',
        json={
            'id':1,
            'name':'wrongName',
            'status':'borrowed for min',
            'date_updated':str(datetime(2022,4,1))
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,409)
        self.assertFalse(data['success'])
    
    #move item
    def test_move_item(self):
        self.prep_insert_container('container1')
        self.prep_insert_container('container2')
        self.prep_insert_item('shortliveditem')
        result=self.client.patch('/items/update',
        json={
            'id':1,
            'name':'shortliveditem',
            'container_id':1,
            'date_updated':str(datetime(2022,4,1))
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['container'],1)

        result=self.client.patch('/items/update',
        json={
            'id':1,
            'name':'shortliveditem',
            'container_id':2,
            'date_updated':str(datetime(2022,4,1))
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['container'],2)


    #DELETE items/<int:id>
    def test_delete_item(self):
        self.prep_insert_item('shortliveditem')
        self.assertIsNotNone(Item.query.filter(Item.id==1).one_or_none())
        result=self.client.delete('/items/1')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertIsNone(Item.query.filter(Item.id==1).one_or_none())

    def test_delete_item_not_found(self):
        result=self.client.delete('/items/4321')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    #POST items/search
    def test_item_search(self):
        self.prep_insert_item('shortliveditem')
        result=self.client.post('/items/search',
        json={
            'search_term':'Lived'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data,{
            'success':True,
            'id':1,
            'name':'shortliveditem',
            'location':'over_here',
            'value':3000
            })

    def test_item_search_not_found(self):
        self.prep_insert_item('shortliveditem')
        result=self.client.post('/items/search',
        json={
            'search_term':'quack'
        })
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    

if __name__=="__main__":
    unittest.main()