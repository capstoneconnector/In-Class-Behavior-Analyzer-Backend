from api.auth_views import login, register, logout, request_password_reset
from api.models import Student, Session

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser

rf = RequestFactory()


class UserLoginTests(TestCase):

    def setUp(self):
        u = User.objects.create(username='test_user', email='test@test.com')
        u.set_password('test_password1234')
        u.save()

    def test_user_login_success(self):
        mock_request = rf.post('api/login/', {
            'username': 'test_user', 'password': 'test_password1234'
        })
        response = login(mock_request)

        self.assertTrue('"session_id"' in response.content.decode('utf-8'))
        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_wrong_request_type(self):
        mock_request = rf.get('api/login/', {
            'username': 'test_user', 'password': 'test_password1234'
        })
        response = login(mock_request)

        self.assertTrue('"error_id": 101' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('api/login/', {
            'username': 'test_user'
        })
        response = login(mock_request)

        self.assertTrue('"error_id": 103' in response.content.decode('utf-8'))

    def test_user_does_not_exist(self):
        mock_request = rf.post('api/login/', {
            'username': 'test_user1234', 'password': 'test_password1234'
        })
        response = login(mock_request)

        self.assertTrue('"error_id": 104' in response.content.decode('utf-8'))


class UserRegisterTests(TestCase):

    mock_request = rf.post('api/register/', {
        'username': 'test_user1', 'password': 'test_password1234', 'email': 'test1@test.com', 'first_name': 'test1',
        'last_name': 'test1'
    })

    def setUp(self):
        u = User.objects.create(username='test_user', email='test@test.com')
        u.set_password('test_password1234')
        u.save()

    def test_user_created(self):
        register(UserRegisterTests.mock_request)

        u = User.objects.get(username='test_user1')
        self.assertIsNotNone(u)

    def test_password_encrypted(self):
        register(UserRegisterTests.mock_request)

        u = User.objects.get(username='test_user1')
        self.assertIsNot(u.password, 'test_password1234')

    def test_student_created(self):
        register(UserRegisterTests.mock_request)

        u = User.objects.get(username='test_user1')
        s = Student.objects.get(user=u)
        self.assertIsNotNone(s)

    def test_wrong_request_type(self):
        mock_request = rf.get('api/register/', {
            'username': 'test_user1', 'password': 'test_password1234', 'email': 'test1@test.com', 'first_name': 'test1',
            'last_name': 'test1'
        })
        response = register(mock_request)

        self.assertTrue('"error_id": 101' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('api/register/',
                               {'username': 'test_user2', 'email': 'test2@test.com'})
        response = register(mock_request)

        self.assertTrue('"error_id": 103' in response.content.decode('utf-8'))

    def test_username_already_exists(self):
        mock_request = rf.post('api/register/', {
            'username': 'test_user', 'password': 'test_password1234', 'email': 'test1@test.com', 'first_name': 'test1',
            'last_name': 'test1'
        })
        response = register(mock_request)

        self.assertTrue('"error_id": 106' in response.content.decode('utf-8'))

    def test_not_strong_enough_password(self):
        mock_request = rf.post('api/register/', {
            'username': 'test_user1', 'password': 'A', 'email': 'test1@test.com', 'first_name': 'test1',
            'last_name': 'test1'
        })
        response = register(mock_request)

        self.assertTrue('"error_id": 111' in response.content.decode('utf-8'))


class UserLogoutTests(TestCase):

    def setUp(self):
        register_request = rf.post('api/register', {
            'username': 'test_user', 'password': 'test_password1234', 'email': 'test@test.com', 'first_name': 'test',
            'last_name': 'test'
        })
        register(register_request)

        login_request = rf.post('/api/login', {
            'username': 'test_user', 'password': 'test_password1234'
        })
        response = login(login_request)
        self.session_id = response.content.decode('utf-8').split('"session_id": "')[1].split('"')[0]

        self.logout_request = rf.get('/api/logout', {
            'session_id': self.session_id
        })

    def test_success_status(self):
        response = logout(self.logout_request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_logout_remove_session_id(self):
        logout(self.logout_request)

        test_sessions = Session.objects.filter(id=self.session_id)
        self.assertTrue(len(test_sessions) == 0)

        user_sessions = Session.objects.filter(user=User.objects.get(username='test_user'))
        self.assertTrue(len(user_sessions) == 0)

    def test_wrong_request_method(self):
        mock_request = rf.post('/api/logout', {
            'session_id': self.session_id
        })
        response = logout(mock_request)

        self.assertTrue('"error_id": 101' in response.content.decode('utf-8'))

    def test_not_enough_GET_data(self):
        mock_request = rf.get('/api/logout', {})
        response = logout(mock_request)

        self.assertTrue('"error_id": 100' in response.content.decode('utf-8'))


class RequestPasswordResetTests(TestCase):

    def setUp(self):
        register_request = rf.post('api/auth/register', {
            'username': 'test_user', 'password': 'test_password1234', 'email': 'test@test.com', 'first_name': 'test',
            'last_name': 'test'
        })
        register(register_request)

        self.request_password_reset_request = rf.get('/api/auth/request_password_reset/test_user')

    def test_success_status(self):
        response = request_password_reset(self.request_password_reset_request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-u'))
