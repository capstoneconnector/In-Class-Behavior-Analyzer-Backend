from api.survey_views import end_session_create_survey_instance, get_all_open_survey_instances, get_survey_by_id, add_responses_to_survey
from api.models import Student, Session, Class, DayLookup, ClassEnrollment, Survey, SurveyResponse, SurveyQuestion, Position, SurveyInstance, SurveyPositionInstance, SurveyQuestionInstance

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

import json
import datetime

rf = RequestFactory()


class EndSessionCreateSurveyInstanceTests(TestCase):

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
            start_time=timezone.now(),
            end_time=timezone.now() + datetime.timedelta(hours=1)
        )
        self.new_class.save()

        ClassEnrollment.objects.create(class_enrolled=self.new_class, student=self.new_student)

        self.new_survey = Survey.objects.create(admin=self.new_admin, associated_class=self.new_class)
        self.new_survey.save()

        self.new_survey_question = SurveyQuestion.objects.create(survey=self.new_survey, type='SA', prompt_text='Test Question')

        self.new_position = Position.objects.create(student=self.new_student, timestamp=timezone.now() + datetime.timedelta(minutes=10), x=1, y=1)

        self.request = rf.post('/api/survey/generate?session_id=' + str(self.session_id), {
            'class': str(self.new_class.id)
        })

    def test_success_status(self):
        response = end_session_create_survey_instance(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_survey_retrieved(self):
        end_session_create_survey_instance(self.request)

        self.assertEqual(1, len(SurveyInstance.objects.filter(survey=self.new_survey)))
        survey_instance = SurveyInstance.objects.get(survey=self.new_survey)

        self.assertEqual(1, len(SurveyQuestionInstance.objects.filter(survey_instance=survey_instance)))
        self.assertEqual(1, len(SurveyPositionInstance.objects.filter(survey_instance=survey_instance)))

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/survey/generate?session_id=' + str(self.session_id), {
            'class': str(self.new_class.id)
        })
        response = end_session_create_survey_instance(mock_request)

        self.assertTrue('"error_id": 501' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/survey/generate', {
            'class': str(self.new_class.id)
        })
        response = end_session_create_survey_instance(mock_request)

        self.assertTrue('"error_id": 500' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/survey/generate?session_id=' + str(self.session_id), {})
        response = end_session_create_survey_instance(mock_request)

        self.assertTrue('"error_id": 503' in response.content.decode('utf-8'))

    def test_bad_class_lookup(self):
        mock_request = rf.post('/api/survey/generate?session_id=' + str(self.session_id), {
            'class': 1111
        })
        response = end_session_create_survey_instance(mock_request)

        self.assertTrue('"error_id": 506' in response.content.decode('utf-8'))

    def test_no_survey_with_class(self):
        self.new_survey.delete()
        response = end_session_create_survey_instance(self.request)

        self.assertTrue('"error_id": 504' in response.content.decode('utf-8'))

    def test_survey_instance_already_exists(self):
        new_survey = SurveyInstance.objects.create(survey=self.new_survey, student=self.new_student, date_generated=timezone.now().date())
        new_survey.save()
        response = end_session_create_survey_instance(self.request)

        self.assertTrue('"error_id": 510' in response.content.decode('utf-8'))


class OpenSurveyInstancesTests(TestCase):

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
            start_time=timezone.now(),
            end_time=timezone.now() + datetime.timedelta(hours=1)
        )
        self.new_class.save()

        ClassEnrollment.objects.create(class_enrolled=self.new_class, student=self.new_student)

        self.new_survey = Survey.objects.create(admin=self.new_admin, associated_class=self.new_class)
        self.new_survey.save()

        self.new_survey_question = SurveyQuestion.objects.create(survey=self.new_survey, type='SA',
                                                                 prompt_text='Test Question')

        self.new_survey_instance = SurveyInstance.objects.create(survey=self.new_survey, student=self.new_student)

        self.new_question_instance = SurveyQuestionInstance.objects.create(survey_instance=self.new_survey_instance, question=self.new_survey_question)

        self.request = rf.post('/api/survey/open_surveys?session_id=' + str(self.session_id), {})

    def test_success_status(self):
        response = get_all_open_survey_instances(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual('success', json_obj['status'])

    def test_correct_open_surveys(self):
        response = get_all_open_survey_instances(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual(1, len(json_obj['data']))
        self.assertEqual(self.new_survey.id, json_obj['data'][0]['survey'])
        self.assertEqual(self.new_survey_instance.id, json_obj['data'][0]['id'])
        self.assertEqual(timezone.now().date().strftime('%Y-%m-%d'), json_obj['data'][0]['date_generated'])

    def test_correct_closed_surveys(self):
        SurveyResponse.objects.create(survey_entry=self.new_question_instance, response='Test Response')
        response = get_all_open_survey_instances(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual(0, len(json_obj['data']))

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/survey/open_surveys?session_id=' + str(self.session_id), {})
        response = get_all_open_survey_instances(mock_request)

        self.assertTrue('"error_id": 501' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/survey/open_surveys', {
            'class': str(self.new_class.id)
        })
        response = get_all_open_survey_instances(mock_request)

        self.assertTrue('"error_id": 500' in response.content.decode('utf-8'))


class GetSurveyById(TestCase):

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
            start_time=timezone.now(),
            end_time=timezone.now() + datetime.timedelta(hours=1)
        )
        self.new_class.save()

        ClassEnrollment.objects.create(class_enrolled=self.new_class, student=self.new_student)

        self.new_survey = Survey.objects.create(admin=self.new_admin, associated_class=self.new_class)
        self.new_survey.save()

        self.new_survey_question = SurveyQuestion.objects.create(survey=self.new_survey, type='SA',
                                                                 prompt_text='Test Question')

        self.new_survey_instance = SurveyInstance.objects.create(survey=self.new_survey, student=self.new_student)

        self.new_question_instance = SurveyQuestionInstance.objects.create(survey_instance=self.new_survey_instance,
                                                                           question=self.new_survey_question)

        self.request = rf.post('/api/survey/get?session_id=' + str(self.session_id), {
            'survey_id': self.new_survey_instance.id,
        })

    def test_success_status(self):
        response = get_survey_by_id(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual('success', json_obj['status'])

    def test_correct_data_returned(self):
        response = get_survey_by_id(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual(1, json_obj['data']['survey_instance']['id'])
        self.assertEqual(0, len(json_obj['data']['positions']))
        self.assertEqual(1, len(json_obj['data']['questions']))

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/survey/get?session_id=' + str(self.session_id), {})
        response = get_survey_by_id(mock_request)

        self.assertTrue('"error_id": 501' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/survey/get', {
            'class': str(self.new_class.id)
        })
        response = get_survey_by_id(mock_request)

        self.assertTrue('"error_id": 500' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/survey/get?session_id=' + str(self.session_id), {})
        response = get_survey_by_id(mock_request)

        self.assertTrue('"error_id": 503' in response.content.decode('utf-8'))

    def test_survey_does_not_exist(self):
        mock_request = rf.post('/api/survey/get?session_id=' + str(self.session_id), {
            'survey_id': 111
        })
        response = get_survey_by_id(mock_request)

        self.assertTrue('"error_id": 504' in response.content.decode('utf-8'))

    def test_invalid_student_for_survey(self):
        new_user = User.objects.create(username='test_user1', email='test_user1@test.com', first_name='test', last_name='test')
        new_student = Student.objects.create(user=new_user)
        new_session = Session.objects.create(user=new_user)

        mock_request = rf.post('/api/survey/get?session_id=' + str(new_session.id), {
            'survey_id': self.new_survey_instance.id
        })
        response = get_survey_by_id(mock_request)

        self.assertTrue('"error_id": 509' in response.content.decode('utf-8'))


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
            start_time=timezone.now(),
            end_time=timezone.now() + datetime.timedelta(hours=1)
        )
        self.new_class.save()

        ClassEnrollment.objects.create(class_enrolled=self.new_class, student=self.new_student)

        self.new_survey = Survey.objects.create(admin=self.new_admin, associated_class=self.new_class)
        self.new_survey.save()

        self.new_survey_question = SurveyQuestion.objects.create(survey=self.new_survey, type='SA',
                                                                 prompt_text='Test Question')
        self.new_survey_question1 = SurveyQuestion.objects.create(survey=self.new_survey, type='RA',
                                                                  prompt_text='Test Question 1')

        self.new_survey_instance = SurveyInstance.objects.create(survey=self.new_survey, student=self.new_student)

        self.new_question_instance = SurveyQuestionInstance.objects.create(survey_instance=self.new_survey_instance,
                                                                           question=self.new_survey_question)
        self.new_question_instance1 = SurveyQuestionInstance.objects.create(survey_instance=self.new_survey_instance,
                                                                          question=self.new_survey_question1)

        self.new_response = SurveyResponse.objects.create(survey_entry=self.new_question_instance1, response='Test Update')

        self.request = rf.post('/api/survey/respond?session_id=' + str(self.session_id), {
            'survey_id': self.new_survey_instance.id,
            1: 'test response',
            2: 'test update again',
            111: 'test bad id'
        })

    def test_success_status(self):
        response = add_responses_to_survey(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual('success', json_obj['status'])

    def test_correct_addition(self):
        response = add_responses_to_survey(self.request)
        json_obj = json.loads(response.content.decode('utf-8'))

        self.assertEqual('bad id', json_obj['data']['111'])
        self.assertEqual('created', json_obj['data']['1'])
        self.assertEqual('updated', json_obj['data']['2'])

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/survey/respond?session_id=' + str(self.session_id), {
            'survey_id': self.new_survey_instance.id,
            1: 'test response',
            2: 'test update again',
            111: 'test bad id'
        })
        response = add_responses_to_survey(mock_request)

        self.assertTrue('"error_id": 501' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/survey/respond', {
            'survey_id': self.new_survey_instance.id,
            1: 'test response',
            2: 'test update again',
            111: 'test bad id'
        })
        response = add_responses_to_survey(mock_request)

        self.assertTrue('"error_id": 500' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/survey/respond?session_id=' + str(self.session_id), {
            1: 'test response',
            2: 'test update again',
            111: 'test bad id'
        })
        response = add_responses_to_survey(mock_request)

        self.assertTrue('"error_id": 503' in response.content.decode('utf-8'))

    def test_survey_does_not_exist(self):
        mock_request = rf.post('/api/survey/respond?session_id=' + str(self.session_id), {
            'survey_id': 111,
            1: 'test response',
            2: 'test update again',
            111: 'test bad id'
        })
        response = add_responses_to_survey(mock_request)

        self.assertTrue('"error_id": 504' in response.content.decode('utf-8'))

    def test_student_does_not_belong_to_student(self):
        new_user = User.objects.create(username='test_user1', email='test_user1@test.com', first_name='test', last_name='test')
        new_student = Student.objects.create(user=new_user)
        new_session = Session.objects.create(user=new_user)

        mock_request = rf.post('/api/survey/respond?session_id=' + str(new_session.id), {
            'survey_id': self.new_survey_instance.id,
            1: 'test response',
            2: 'test update again',
            111: 'test bad id'
        })
        response = add_responses_to_survey(mock_request)

        self.assertTrue('"error_id": 509' in response.content.decode('utf-8'))