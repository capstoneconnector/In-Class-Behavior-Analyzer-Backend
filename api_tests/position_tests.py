from api.position_views import position_create, position_select_all, position_select_id, position_summary
from api.models import Student, Session, Position

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

import json
import uuid
from datetime import datetime, timedelta

rf = RequestFactory()


class PositionCreateTests(TestCase):

    def setUp(self):
        self.new_user = User.objects.create(username='test_user', email='test@test.com', first_name='first_test',
                                            last_name='last_test')
        self.new_user.set_password('test_password1234')
        self.new_user.save()

        self.new_student = Student.objects.create(user=self.new_user)
        self.new_student.save()

        new_session = Session.objects.create(user=self.new_user)
        new_session.save()
        self.session_id = new_session.id

        self.position_request = rf.get('/api/position/create', {
            'session_id': self.session_id,
            'x': 1,
            'y': 1
        })

    def test_position_created(self):
        position_create(self.position_request)

        self.assertEqual(1, len(Position.objects.all()))

    def test_success_status(self):
        response = position_create(self.position_request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_wrong_request_type(self):
        mock_request = rf.post('/api/position/create?session_id=' + str(self.session_id), {
            'x': 1,
            'y': 1
        })

        response = position_create(mock_request)

        self.assertTrue('"error_id": 301' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.get('/api/position/create', {
            'x': 1,
            'y': 1
        })

        response = position_create(mock_request)

        self.assertTrue('"error_id": 300' in response.content.decode('utf-8'))

    def test_not_enough_GET_data(self):
        mock_request = rf.get('/api/position/create', {
            'session_id': str(self.session_id),
            'x': 1,
        })

        response = position_create(mock_request)

        self.assertTrue('"error_id": 302' in response.content.decode('utf-8'))


class PositionSelectAllTests(TestCase):

    def setUp(self):
        self.new_user = User.objects.create(username='test_user', email='test@test.com', first_name='first_test',
                                            last_name='last_test')
        self.new_user.set_password('test_password1234')
        self.new_user.save()

        self.new_student = Student.objects.create(user=self.new_user)
        self.new_student.save()

        new_session = Session.objects.create(user=self.new_user)
        new_session.save()
        self.session_id = new_session.id

        new_position_1 = Position.objects.create(x=1, y=1, student=self.new_student, timestamp=datetime.now())
        new_position_1.save()

        new_position_2 = Position.objects.create(x=2, y=2, student=self.new_student, timestamp=datetime.now())
        new_position_2.save()

        self.request = rf.get('/api/position/all', {
            'session_id': str(self.session_id)
        })

    def test_success_status(self):
        response = position_select_all(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_objects_retrieved(self):
        response = position_select_all(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual(2, len(json_obj['data']))

    def test_wrong_request_type(self):
        mock_request = rf.post('/api/position/select/all?session_id=' + str(self.session_id))
        response = position_select_all(mock_request)

        self.assertTrue('"error_id": 301' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.get('/api/position/select/all')
        response = position_select_all(mock_request)

        self.assertTrue('"error_id": 300' in response.content.decode('utf-8'))


class PositionSelectIDTests(TestCase):

    def setUp(self):
        self.new_user = User.objects.create(username='test_user', email='test@test.com', first_name='first_test',
                                            last_name='last_test')
        self.new_user.set_password('test_password1234')
        self.new_user.save()

        self.new_student = Student.objects.create(user=self.new_user)
        self.new_student.save()

        new_session = Session.objects.create(user=self.new_user)
        new_session.save()
        self.session_id = new_session.id

        new_position_1 = Position.objects.create(x=1, y=1, student=self.new_student, timestamp=datetime.now())
        new_position_1.save()
        self.position_id = new_position_1.id

        self.request = rf.get('/api/position/select', {
            'session_id': str(self.session_id),
            'position_id': str(self.position_id)
        })

    def test_success_stats(self):
        response = position_select_id(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_objects_retrieved(self):
        response = position_select_id(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertTrue('x' in json_obj['data'])
        self.assertTrue('y' in json_obj['data'])
        self.assertTrue('id' in json_obj['data'])
        self.assertTrue('student' in json_obj['data'])
        self.assertTrue('timestamp' in json_obj['data'])

    def test_wrong_request_type(self):
        mock_request = rf.post('/api/position/select?session_id=' + str(self.session_id), {
            'position_id': str(self.position_id)
        })
        response = position_select_id(mock_request)

        self.assertTrue('"error_id": 301' in response.content.decode('utf-8'))

    def test_no_logged_in_used(self):
        mock_request = rf.get('/api/position/select', {
            'position_id': str(self.position_id)
        })
        response = position_select_id(mock_request)

        self.assertTrue('"error_id": 300' in response.content.decode('utf-8'))

    def test_not_enough_GET_data(self):
        mock_request = rf.get('/api/position/select', {
            'session_id': str(self.session_id)
        })
        response = position_select_id(mock_request)

        self.assertTrue('"error_id": 302' in response.content.decode('utf-8'))

    def test_position_does_not_exist(self):
        mock_request = rf.get('/api/position/select', {
            'session_id': str(self.session_id),
            'position_id': 111
        })
        response = position_select_id(mock_request)

        self.assertTrue('"error_id": 303' in response.content.decode('utf-8'))

    def test_position_does_not_belong_to_student(self):
        new_user = User.objects.create(username='test_user1', email='test1@test.com', first_name='first_test1',
                                            last_name='last_test1')
        new_user.set_password('test_password1234')
        new_user.save()

        new_student = Student.objects.create(user=new_user)
        new_student.save()

        new_position = Position.objects.create(x=1, y=1, student=new_student, timestamp=datetime.now())
        new_position.save()

        mock_request = rf.get('/api/position/select', {
            'session_id': str(self.session_id),
            'position_id': str(new_position.id)
        })
        response = position_select_id(mock_request)

        self.assertTrue('"error_id": 304' in response.content.decode('utf-8'))


class PositionSummaryTests(TestCase):

    def setUp(self):
        self.new_user = User.objects.create(username='test_user', email='test@test.com', first_name='first_test',
                                            last_name='last_test')
        self.new_user.set_password('test_password1234')
        self.new_user.save()

        self.new_student = Student.objects.create(user=self.new_user)
        self.new_student.save()

        new_session = Session.objects.create(user=self.new_user)
        new_session.save()
        self.session_id = new_session.id

        new_position_1 = Position.objects.create(x=1, y=1, student=self.new_student, timestamp=datetime.now())
        new_position_1.save()

        new_position_2 = Position.objects.create(x=2, y=2, student=self.new_student, timestamp=datetime.now() + timedelta(hours=1))
        new_position_2.save()

        self.request = rf.get('/api/position/summary', {
            'session_id': str(self.session_id),
            'start_time': str(datetime.now() - timedelta(minutes=1)),
            'end_time': str(datetime.now() + timedelta(hours=2))
        })

    def test_success_status(self):
        response = position_summary(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_retrieved_objects(self):
        response = position_summary(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual(2, len(json_obj['data']))

    def test_retrieve_within_date_range(self):
        request = rf.get('/api/position/summary', {
            'session_id': str(self.session_id),
            'start_time': str(datetime.now() - timedelta(minutes=1)),
            'end_time': str(datetime.now() + timedelta(minutes=30))
        })
        response = position_summary(request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual(1, len(json_obj['data']))

    def test_wrong_request_type(self):
        request = rf.post('/api/position/summary', {
            'session_id': str(self.session_id),
            'start_time': str(datetime.now() - timedelta(minutes=1)),
            'end_time': str(datetime.now() + timedelta(minutes=30))
        })
        response = position_summary(request)

        self.assertTrue('"error_id": 301' in response.content.decode('utf-8'))

    def test_no_logged_in_used(self):
        request = rf.get('/api/position/summary', {
            'start_time': str(datetime.now() - timedelta(minutes=1)),
            'end_time': str(datetime.now() + timedelta(minutes=30))
        })
        response = position_summary(request)

        self.assertTrue('"error_id": 300' in response.content.decode('utf-8'))

    def test_not_enough_GET_data(self):
        request = rf.get('/api/position/summary', {
            'session_id': str(self.session_id),
            'end_time': str(datetime.now() + timedelta(minutes=30))
        })
        response = position_summary(request)

        self.assertTrue('"error_id": 302' in response.content.decode('utf-8'))

    def test_invalid_datetime_string(self):
        request = rf.get('/api/position/summary', {
            'session_id': str(self.session_id),
            'start_time': '2019-03-26 13:04:65',
            'end_time': str(datetime.now() + timedelta(minutes=30))
        })
        response = position_summary(request)

        self.assertTrue('"error_id": 305' in response.content.decode('utf-8'))

    def test_empty_datetime_string(self):
        request = rf.get('/api/position/summary', {
            'session_id': str(self.session_id),
            'start_time': '',
            'end_time': str(datetime.now() + timedelta(minutes=30))
        })
        response = position_summary(request)

        self.assertTrue('"error_id": 306' in response.content.decode('utf-8'))
