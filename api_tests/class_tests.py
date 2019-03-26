from api.class_views import class_select_all, class_summarize_movement
from api.models import Student, Session, Class, DayLookup, ClassEnrollment, Position

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

import json
import datetime

rf = RequestFactory()


class ClassSelectAllTests(TestCase):

    def setUp(self):
        self.new_user = User.objects.create(username='test_user', email='test@test.com', first_name='first_test',
                                            last_name='last_test')
        self.new_user.set_password('test_password1234')
        self.new_user.save()

        self.new_admin = User.objects.create(username='test_admin', email='admin@test.com', first_name='first_admin',
                                             last_name='last_admin')
        self.new_admin.set_password('admin_password1234')
        self.new_admin.save()

        self.new_student = Student.objects.create(user=self.new_user)
        self.new_student.save()

        new_session = Session.objects.create(user=self.new_user)
        new_session.save()
        self.session_id = new_session.id

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in range(len(days)):
            new_day = DayLookup.objects.create(id=i, name=days[i])
            new_day.save()

        self.new_class = Class.objects.create(
            title='Test Class',
            admin=self.new_admin,
            semester='FL',
            section=1,
            year=2019,
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now() + datetime.timedelta(hours=1)
        )
        self.new_class.save()

        ClassEnrollment.objects.create(class_enrolled=self.new_class, student=self.new_student)

        self.request = rf.get('/api/class/select/all', {
            'session_id': str(self.session_id)
        })

    def test_success_status(self):
        response = class_select_all(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_class_retrieved(self):
        response = class_select_all(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertTrue('data' in json_obj)
        self.assertEqual(1, len(json_obj['data']))

    def test_wrong_request_type(self):
        mock_request = rf.post('/api/class/select/all', {
            'session_id': str(self.session_id)
        })
        response = class_select_all(mock_request)

        self.assertTrue('"error_id": 401' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.get('/api/class/select/all')
        response = class_select_all(mock_request)

        self.assertTrue('"error_id": 400' in response.content.decode('utf-8'))


class ClassSummerizeMovement(TestCase):

    def setUp(self):
        self.new_user = User.objects.create(username='test_user', email='test@test.com', first_name='first_test',
                                            last_name='last_test')
        self.new_user.set_password('test_password1234')
        self.new_user.save()

        self.new_admin = User.objects.create(username='test_admin', email='admin@test.com', first_name='first_admin',
                                             last_name='last_admin')
        self.new_admin.set_password('admin_password1234')
        self.new_admin.save()

        self.new_student = Student.objects.create(user=self.new_user)
        self.new_student.save()

        new_session = Session.objects.create(user=self.new_user)
        new_session.save()
        self.session_id = new_session.id

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in range(len(days)):
            new_day = DayLookup.objects.create(id=i, name=days[i])
            new_day.save()

        self.new_class = Class.objects.create(
            title='Test Class',
            admin=self.new_admin,
            semester='FL',
            section=1,
            year=2019,
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now() + datetime.timedelta(hours=1),
        )

        for i in range(len(days)):
            self.new_class.days_of_the_week.add(DayLookup.objects.get(id=1))

        self.new_class.save()

        ClassEnrollment.objects.create(class_enrolled=self.new_class, student=self.new_student)

        self.new_position = Position.objects.create(x=1, y=1, student=self.new_student, timestamp=datetime.datetime.now() + datetime.timedelta(minutes=30))

        self.request = rf.post('/api/class/movement_summary?session_id=' + str(self.session_id), {
            'class': str(self.new_class.id),
            'start_date': (datetime.date.today() - datetime.timedelta(days=1)).strftime('%m/%d/%Y'),
            'end_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
        })

    def test_success_status(self):
        response = class_summarize_movement(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_class_position_retrieve(self):
        response = class_summarize_movement(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        print(json_obj)

        self.assertEqual(1, len(json_obj['data']))

        today_date = datetime.date.today().strftime('%Y-%m-%d')
        self.assertEqual(1, len(json_obj['data'][today_date]))

        self.assertEqual(self.new_position.x, json_obj['data'][today_date][0]['x'])

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/class/movement_summary?session_id=' + str(self.session_id), {
            'class': str(self.new_class.id),
            'start_date': (datetime.date.today() - datetime.timedelta(days=1)).strftime('%m/%d/%Y'),
            'end_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
        })
        response = class_summarize_movement(mock_request)

        self.assertTrue('"error_id": 401' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/class/movement_summary', {
            'class': str(self.new_class.id),
            'start_date': (datetime.date.today() - datetime.timedelta(days=1)).strftime('%m/%d/%Y'),
            'end_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
        })
        response = class_summarize_movement(mock_request)

        self.assertTrue('"error_id": 400' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/class/movement_summary?session_id=' + str(self.session_id), {
            'class': str(self.new_class.id),
            'end_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
        })
        response = class_summarize_movement(mock_request)

        self.assertTrue('"error_id": 403' in response.content.decode('utf-8'))

    def test_class_does_not_exist(self):
        mock_request = rf.post('/api/class/movement_summary?session_id=' + str(self.session_id), {
            'class': '0314864b-1f77-4356-a2f6-d9dfe933ae09',
            'start_date': (datetime.date.today() - datetime.timedelta(days=1)).strftime('%m/%d/%Y'),
            'end_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%m/%d/%Y')
        })
        response = class_summarize_movement(mock_request)

        self.assertTrue('"error_id": 407' in response.content.decode('utf-8'))