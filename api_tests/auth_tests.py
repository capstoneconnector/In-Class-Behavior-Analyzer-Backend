from api.auth_views import login, register, logout, request_password_reset, reset_password
from api.models import Student, Session

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

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

    def test_session_already_exists(self):
        mock_request = rf.post('api/login/', {
            'username': 'test_user', 'password': 'test_password1234'
        })
        first_response = login(mock_request)
        second_response = login(mock_request)

        first_session_id = first_response.content.decode('utf-8').split('"session_id": "')[1].split('"')[0]
        second_session_id = second_response.content.decode('utf-8').split('"session_id": "')[1].split('"')[0]

        self.assertTrue(first_session_id == second_session_id)

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

    def test_wrong_password(self):
        mock_request = rf.post('api/login/', {
            'username': 'test_user', 'password': 'test_password12341'
        })
        response = login(mock_request)

        self.assertTrue('"error_id": 105' in response.content.decode('utf-8'))


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

    def test_user_already_logged_out(self):
        test_session = Session.objects.get(user=User.objects.get(username='test_user'))
        test_session.delete()

        response = logout(self.logout_request)
        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

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

        self.request_password_reset_request = rf.get('/api/auth/request_password_reset/')

    def test_success_status(self):
        response = request_password_reset(self.request_password_reset_request, 'test_user')

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_has_reset_code(self):
        request_password_reset(self.request_password_reset_request, 'test_user')
        test_user = User.objects.get(username='test_user')

        self.assertIsNotNone(Student.objects.get(user=test_user).reset_password_code)

    def test_wrong_request_type(self):
        response = request_password_reset(rf.post('/api/auth/request_password_reset/'), 'test_user')

        self.assertTrue('"error_id": 101' in response.content.decode('utf-8'))

    def test_bad_username(self):
        response = request_password_reset(self.request_password_reset_request, 'test_user2')

        self.assertTrue('"error_id": 104' in response.content.decode('utf-8'))

    def test_reset_code_already_exists(self):
        request_password_reset(self.request_password_reset_request, 'test_user')
        response = request_password_reset(self.request_password_reset_request, 'test_user')

        self.assertTrue('"error_id": 107' in response.content.decode('utf-8'))


class ResetPasswordTests(TestCase):

    def setUp(self):
        register_request = rf.post('api/auth/register', {
            'username': 'test_user', 'password': 'test_password1234', 'email': 'test@test.com', 'first_name': 'test',
            'last_name': 'test'
        })
        register(register_request)
        request_password_reset_request = rf.get('/api/auth/request_password_reset/')
        request_password_reset(request_password_reset_request, 'test_user')

        self.reset_code = Student.objects.get(user=User.objects.get(username='test_user')).reset_password_code
        self.password_reset_request = rf.post('/api/auth/reset_password/', {
            'new_password': 'new_test_password1234'
        })

    def test_success_status(self):
        response = reset_password(self.password_reset_request, self.reset_code)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_password_changed(self):
        reset_password(self.password_reset_request, self.reset_code)
        test_user = User.objects.get(username='test_user')

        self.assertTrue(test_user.check_password('new_test_password1234'))

    def test_wrong_request_type(self):
        request = rf.get('/api/auth/reset_password/', {'new_password': 'new_test_password1234'})
        response = reset_password(request, self.reset_code)

        self.assertTrue('"error_id": 101' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        request = rf.post('/api/auth/reset_password/')
        response = reset_password(request, self.reset_code)

        self.assertTrue('"error_id": 103' in response.content.decode('utf-8'))

    def test_bad_reset_code(self):
        response = reset_password(self.password_reset_request, '123456')

        self.assertTrue('"error_id": 108' in response.content.decode('utf-8'))

    def test_no_reset_code(self):
        test_student = Student.objects.get(user=User.objects.get(username='test_user'))
        test_student.reset_password_code = None
        test_student.save()

        response = reset_password(self.password_reset_request, self.reset_code)

        self.assertTrue('"error_id": 108' in response.content.decode('utf-8'))


