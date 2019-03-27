from api.models import Feedback
from api.feedback_views import feedback_create

from django.test import TestCase
from django.test.client import RequestFactory

rf = RequestFactory()


class FeedbackCreateTests(TestCase):

    def setUp(self):
        self.request = rf.post('/api/feedback/submit', {
            'feedback': 'This is the text of a test feedback.'
        })

    def test_success_status(self):
        response = feedback_create(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_feedback_created(self):
        self.assertEqual(0, len(Feedback.objects.all()))

        feedback_create(self.request)

        self.assertEqual(1, len(Feedback.objects.all()))

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/feedback/submit', {
            'feedback': 'This is the text of a test feedback.'
        })
        response = feedback_create(mock_request)

        self.assertTrue('"error_id": 601' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/feedback/submit', {})
        response = feedback_create(mock_request)

        self.assertTrue('"error_id": 603' in response.content.decode('utf-8'))