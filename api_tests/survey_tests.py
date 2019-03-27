from api.survey_views import survey_get_by_class, survey_response_add
from api.models import Student, Session, Class, DayLookup, ClassEnrollment, Survey, SurveyResponse, SurveyQuestion

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

import json
import datetime

rf = RequestFactory()


class SurveySelectByClassTests(TestCase):

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

        self.new_survey = Survey.objects.create(admin=self.new_admin, associated_class=self.new_class)
        self.new_survey.save()

        self.new_survey_question = SurveyQuestion.objects.create(survey=self.new_survey, type='SA', prompt_text='Test Question')

        self.request = rf.post('/api/survey/select?session_id=' + str(self.session_id), {
            'class': str(self.new_class.id)
        })

    def test_success_status(self):
        response = survey_get_by_class(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_survey_retrieved(self):
        response = survey_get_by_class(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        print(json_obj)

        self.assertTrue('data' in json_obj)
        self.assertEqual(str(self.new_admin.id), json_obj['data']['admin'])
        self.assertEqual(str(self.new_survey.id), json_obj['data']['id'])
        self.assertEqual(1, len(json_obj['data']['questions']))

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/survey/select?session_id=' + str(self.session_id), {
            'class': str(self.new_class.id)
        })
        response = survey_get_by_class(mock_request)

        self.assertTrue('"error_id": 501' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/survey/select?', {
            'class': str(self.new_class.id)
        })
        response = survey_get_by_class(mock_request)

        self.assertTrue('"error_id": 500' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/survey/select?session_id=' + str(self.session_id), {})
        response = survey_get_by_class(mock_request)

        self.assertTrue('"error_id": 503' in response.content.decode('utf-8'))

    def test_bad_class_lookup(self):
        mock_request = rf.post('/api/survey/select?session_id=' + str(self.session_id), {
            'class': 111
        })
        response = survey_get_by_class(mock_request)

        self.assertTrue('"error_id": 506' in response.content.decode('utf-8'))

    def test_no_survey_with_class(self):
        self.new_survey.delete()
        response = survey_get_by_class(self.request)

        self.assertTrue('"error_id": 504' in response.content.decode('utf-8'))


class SurveyResponseAddTests(TestCase):

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

        self.new_survey = Survey.objects.create(admin=self.new_admin, associated_class=self.new_class)
        self.new_survey.save()

        self.new_survey_question = SurveyQuestion.objects.create(survey=self.new_survey, type='SA',
                                                                 prompt_text='Test Question')

        self.request = rf.post('/api/survey/select?session_id=' + str(self.session_id), {
            'survey': str(self.new_survey.id),
            str(self.new_survey_question.id): 'Test Response',
            '15': 'Test Question Does Not Exist'
        })

    def test_success_status(self):
        response = survey_response_add(self.request)
        print(response.content.decode('utf-8'))

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_correct_addition(self):
        response = survey_response_add(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual('Question does not exist', json_obj['data']['15'])
        self.assertEqual('Test Response', json_obj['data'][str(self.new_survey_question.id)]['response'])

        survey_responses = SurveyResponse.objects.filter(student=self.new_student)
        self.assertEqual(1, len(survey_responses))

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/survey/select?session_id=' + str(self.session_id), {
            'survey': str(self.new_survey.id),
            str(self.new_survey_question.id): 'Test Response',
            'Bad+UUID': 'Test Bad UUID',
            '28c604a8-0518-4a89-afd7-3028f01d0f12': 'Test Question Does Not Exist'
        })
        response = survey_response_add(mock_request)

        self.assertTrue('"error_id": 501' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/survey/select', {
            'survey': str(self.new_survey.id),
            str(self.new_survey_question.id): 'Test Response',
            'Bad+UUID': 'Test Bad UUID',
            '28c604a8-0518-4a89-afd7-3028f01d0f12': 'Test Question Does Not Exist'
        })
        response = survey_response_add(mock_request)

        self.assertTrue('"error_id": 500' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/survey/select?session_id=' + str(self.session_id), {
            str(self.new_survey_question.id): 'Test Response',
            'Bad+UUID': 'Test Bad UUID',
            '28c604a8-0518-4a89-afd7-3028f01d0f12': 'Test Question Does Not Exist'
        })
        response = survey_response_add(mock_request)

        self.assertTrue('"error_id": 503' in response.content.decode('utf-8'))

    def test_survey_does_not_exist(self):
        mock_request = rf.post('/api/survey/select?session_id=' + str(self.session_id), {
            'survey': 111,
            str(self.new_survey_question.id): 'Test Response',
            'Bad+UUID': 'Test Bad UUID',
            '28c604a8-0518-4a89-afd7-3028f01d0f12': 'Test Question Does Not Exist'
        })
        response = survey_response_add(mock_request)

        self.assertTrue('"error_id": 504' in response.content.decode('utf-8'))

    def test_survey_response_already_exists(self):
        SurveyResponse.objects.create(student=self.new_student, survey_question=self.new_survey_question, response='Test Response')
        mock_request = rf.post('/api/survey/select?session_id=' + str(self.session_id), {
            'survey': str(self.new_survey.id),
            str(self.new_survey_question.id): 'Test Response',
        })
        response = survey_response_add(mock_request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual('Response already exists', json_obj['data'][str(self.new_survey_question.id)])