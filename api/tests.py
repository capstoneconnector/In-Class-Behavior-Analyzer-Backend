from api import views, models
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
        mock_request.user = AnonymousUser()
        mock_request.session = self.client.session
        response = views.login(mock_request)
        self.assertTrue('"completed": 200' in response.content.decode('utf-8'))

    def test_user_already_logged_in(self):
        u = User.objects.get(username='test_user')
        mock_request = rf.post('api/login/', {
            'username': 'test_user', 'password': 'test_password1234'
        })
        mock_request.user = u
        mock_request.session = self.client.session
        response = views.login(mock_request)
        self.assertTrue('"error_id": 3' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('api/login/', {
            'username': 'test_user'
        })
        mock_request.user = AnonymousUser()
        response = views.login(mock_request)
        self.assertTrue('"error_id": 4' in response.content.decode('utf-8'))

    def test_user_does_not_exist(self):
        mock_request = rf.post('api/login/', {
            'username': 'test_user1234', 'password': 'test_password1234'
        })
        mock_request.user = AnonymousUser()
        response = views.login(mock_request)
        self.assertTrue('"error_id": 2' in response.content.decode('utf-8'))


class UserRegisterTests(TestCase):

    def setUp(self):
        mock_request = rf.post('api/register/', {
            'username': 'test_user', 'password': 'test_password1234', 'email': 'test@test.com'
        })
        mock_request.user = AnonymousUser()
        views.register(mock_request)

    def test_user_created(self):
        u = User.objects.get(username='test_user')
        self.assertIsNotNone(u)

    def test_password_encrypted(self):
        u = User.objects.get(username='test_user')
        self.assertIsNot(u.password, 'test_password1234')

    def test_student_created(self):
        u = User.objects.get(username='test_user')
        s = models.Student.objects.get(user=u)
        self.assertIsNotNone(s)

    def test_user_already_logged_in(self):
        mock_request = rf.post('api/register/',
                               {'username': 'test_user2', 'password': 'test_password1234', 'email': 'test2@test.com'})
        u = User.objects.get(username='test_user')
        mock_request.user = u
        response = views.register(mock_request)
        self.assertTrue('"error_id": 3' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('api/register/',
                               {'username': 'test_user2', 'email': 'test2@test.com'})
        mock_request.user = AnonymousUser()
        response = views.register(mock_request)
        self.assertTrue('"error_id": 4' in response.content.decode('utf-8'))

    def test_not_strong_enough_password(self):
        mock_request = rf.post('api/register/',
                               {'username': 'test_user2', 'password': 'A', 'email': 'test2@test.com'})
        mock_request.user = AnonymousUser()
        response = views.register(mock_request)
        self.assertTrue('"error_id": 6' in response.content.decode('utf-8'))


