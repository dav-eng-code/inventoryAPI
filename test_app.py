import unittest
import json
from os import environ
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import db, Container, Item

class TestInventoryApp(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.testing=True
        self.client=self.app.test_client()
        
        self.app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.app = self.app
        db.init_app(self.app)
        db.drop_all()
        db.create_all()
        


    def tearDown(self):
        c=Container.query.filter(Container.name=='myNewContainer').one_or_none()        
        if not c == None:
            c.delete()
        c=Container.query.filter(Container.name=='shortlivedcontainer').one_or_none()        
        if not c == None:
            c.delete()

    def test_homepage(self):
        result=self.client.get('/')
        data=json.loads(result.data)
        self.assertGreaterEqual(data['Total Items'],0)
        self.assertGreaterEqual(data['Total Containers'],0)

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

    def prep_insert_container(self):
        container = Container(
        name='shortlivedcontainer',
        location='over_there',
        container_value=3000
        )
        container.insert()

    def test_get_container_by_name(self):
        self.prep_insert_container()
        result=self.client.get('/containers/shortlivedcontainer')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['id'],1)
        self.assertEqual(data['name'],'shortlivedcontainer')
        self.assertEqual(data['location'],'over_there')
        self.assertEqual(data['container_value'],3000)

    def test_get_container_by_id(self):
        self.prep_insert_container()
        result=self.client.get('/containers/1')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['id'],1)
        self.assertEqual(data['name'],'shortlivedcontainer')
        self.assertEqual(data['location'],'over_there')
        self.assertEqual(data['container_value'],3000)

    def test_get_container_by_name_not_found(self):
        result=self.client.get('/containers/nonexistantcontainer')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    def test_get_container_by_id_not_found(self):
        result=self.client.get('/containers/4321')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,404)
        self.assertFalse(data['success'])

    def test_add_container(self):
        result=self.client.post('/containers/add',
        json={
            'name':'myNewContainer',
            'location':'somewhere',
            'container_value':'0.55'
        })

    def test_add_container_not_processable(self):
        result=self.client.post('/containers/add')
        data=json.loads(result.data)
        self.assertEqual(result.status_code,422)
        self.assertFalse(data['success'])


if __name__=="__main__":
    unittest.main()