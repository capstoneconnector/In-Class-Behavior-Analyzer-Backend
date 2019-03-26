from api.demographic_views import demographic_create, demographic_update, demographic_delete, demographic_select, demographic_form
from api.models import Student, Session, Demographic, GenderLookup, GradeYearLookup, RaceLookup, EthnicityLookup

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

rf = RequestFactory()


class DemographicCreateTests(TestCase):

    def setUp(self):
        self.new_user = User.objects.create(username='test_user', email='test@test.com', first_name='first_test', last_name='last_test')
        self.new_user.set_password('test_password1234')
        self.new_user.save()

        self.new_student = Student.objects.create(user=self.new_user)
        self.new_student.save()

        new_session = Session.objects.create(user=self.new_user)
        new_session.save()
        self.session_id = new_session.id

        test_gender = GenderLookup.objects.create(name='Test Gender')
        test_gender.save()

        test_grade_year = GradeYearLookup.objects.create(name='Test Grade Year')
        test_grade_year.save()

        test_ethnicity = EthnicityLookup.objects.create(name='Test Ethnicity')
        test_ethnicity.save()

        test_race = RaceLookup.objects.create(name='Test Race')
        test_race.save()

        self.demographic_request = rf.post('/api/demographic/create?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '1',
            'race': '1',
            'major': 'Test Major'
        })

    def test_success_status(self):
        response = demographic_create(self.demographic_request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_demographic_object_exists(self):
        demographic_create(self.demographic_request)

        self.assertTrue(len(Demographic.objects.filter(student=self.new_student)) != 0)

    def test_demographic_object_correct(self):
        demographic_create(self.demographic_request)
        created_demographic = Demographic.objects.get(student=self.new_student)

        self.assertEqual(1, created_demographic.race.id)
        self.assertEqual(1, created_demographic.ethnicity.id)
        self.assertEqual(1, created_demographic.gender.id)
        self.assertEqual(1, created_demographic.grade_year.id)
        self.assertEqual(18, created_demographic.age)
        self.assertEqual('Test Major', created_demographic.major)

    def test_wrong_request_method(self):
        mock_request = rf.get('/api/demographic/create?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '1',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_create(mock_request)

        self.assertTrue('"error_id": 201' in response.content.decode('utf-8'))

    def test_no_session_id(self):
        mock_request = rf.post('/api/demographic/create', {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '1',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_create(mock_request)

        self.assertTrue('"error_id": 200' in response.content.decode('utf-8'))

    def test_demographic_object_already_exists(self):
        demographic_create(self.demographic_request)

        response = demographic_create(self.demographic_request)

        self.assertTrue('"error_id": 204' in response.content.decode('utf-8'))

    def test_not_enough_POST_data(self):
        mock_request = rf.post('/api/demographic/create?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '1',
            'major': 'Test Major'
        })

        response = demographic_create(mock_request)

        self.assertTrue('"error_id": 203' in response.content.decode('utf-8'))

    def test_gender_does_not_exist(self):
        mock_request = rf.post('/api/demographic/create?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '2',
            'grade_year': '1',
            'ethnicity': '1',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_create(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))

    def test_grade_year_does_not_exist(self):
        mock_request = rf.post('/api/demographic/create?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '2',
            'ethnicity': '1',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_create(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))

    def test_race_does_not_exist(self):
        mock_request = rf.post('/api/demographic/create?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '1',
            'race': '2',
            'major': 'Test Major'
        })

        response = demographic_create(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))

    def test_ethnicity_does_not_exist(self):
        mock_request = rf.post('/api/demographic/create?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '2',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_create(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))


class DemographicUpdateTests(TestCase):

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

        test_gender = GenderLookup.objects.create(name='Test Gender')
        test_gender.save()

        test_gender1 = GenderLookup.objects.create(name='Test Gender 2')
        test_gender1.save()

        test_grade_year = GradeYearLookup.objects.create(name='Test Grade Year')
        test_grade_year.save()

        test_grade_year1 = GradeYearLookup.objects.create(name='Test Grade Year 2')
        test_grade_year1.save()

        test_ethnicity = EthnicityLookup.objects.create(name='Test Ethnicity')
        test_ethnicity.save()

        test_ethnicity1 = EthnicityLookup.objects.create(name='Test Ethnicity 2')
        test_ethnicity1.save()

        test_race = RaceLookup.objects.create(name='Test Race')
        test_race.save()

        test_race1 = RaceLookup.objects.create(name='Test Race 2')
        test_race1.save()

        self.test_demographic = Demographic.objects.create(student=self.new_student, age=18, gender=test_gender, grade_year=test_grade_year, race=test_race, ethnicity=test_ethnicity)
        self.test_demographic.save()

        self.demographic_update_request = rf.post('/api/demographic/update?session_id=' + str(self.session_id), {
            'age': 20,
            'race': '2',
            'grade_year': '2',
            'gender': '2',
            'ethnicity': '2',
            'major': 'Test Major 2'
        })

    def test_success_status(self):
        response = demographic_update(self.demographic_update_request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_fields_changed_correctly(self):
        demographic_update(self.demographic_update_request)
        demographic_object = Demographic.objects.get(student=self.new_student)

        self.assertEqual(20, demographic_object.age)
        self.assertEqual('2', str(demographic_object.grade_year.id))

    def test_wrong_request_type(self):
        mock_request = rf.get('/api/demographic/update?session_id=' + str(self.session_id), {
            'age': 20,
            'grade_year': '2'
        })

        response = demographic_update(mock_request)

        self.assertTrue('"error_id": 201' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.post('/api/demographic/update', {
            'age': 20,
            'grade_year': '2'
        })

        response = demographic_update(mock_request)

        self.assertTrue('"error_id": 200' in response.content.decode('utf-8'))

    def test_no_demographic_object(self):
        Demographic.objects.get(student=self.new_student).delete()
        mock_request = rf.post('/api/demographic/update?session_id=' + str(self.session_id), {
            'age': 20,
            'grade_year': '2'
        })

        response = demographic_update(mock_request)

        self.assertTrue('"error_id": 206' in response.content.decode('utf-8'))

    def test_gender_does_not_exist(self):
        mock_request = rf.post('/api/demographic/update?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '3',
            'grade_year': '1',
            'ethnicity': '1',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_update(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))

    def test_grade_year_does_not_exist(self):
        mock_request = rf.post('/api/demographic/update?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '3',
            'ethnicity': '1',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_update(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))

    def test_race_does_not_exist(self):
        mock_request = rf.post('/api/demographic/update?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '1',
            'race': '3',
            'major': 'Test Major'
        })

        response = demographic_update(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))

    def test_ethnicity_does_not_exist(self):
        mock_request = rf.post('/api/demographic/update?session_id=' + str(self.session_id), {
            'age': 18,
            'gender': '1',
            'grade_year': '1',
            'ethnicity': '3',
            'race': '1',
            'major': 'Test Major'
        })

        response = demographic_update(mock_request)

        self.assertTrue('"error_id": 205' in response.content.decode('utf-8'))


class DemographicDeleteTests(TestCase):

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

        test_gender = GenderLookup.objects.create(name='Test Gender')
        test_gender.save()

        test_grade_year = GradeYearLookup.objects.create(name='Test Grade Year')
        test_grade_year.save()

        test_ethnicity = EthnicityLookup.objects.create(name='Test Ethnicity')
        test_ethnicity.save()

        test_race = RaceLookup.objects.create(name='Test Race')
        test_race.save()

        self.test_demographic = Demographic.objects.create(student=self.new_student, age=18, gender=test_gender,
                                                           grade_year=test_grade_year, race=test_race,
                                                           ethnicity=test_ethnicity)
        self.test_demographic.save()

        self.demographic_delete_request = rf.get('/api/demographic/delete?session_id=' + str(self.session_id))

    def test_success_status(self):
        response = demographic_delete(self.demographic_delete_request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_demographic_delete(self):
        demographic_delete(self.demographic_delete_request)

        self.assertEqual(0, len(Demographic.objects.filter(student=self.new_student)))

    def test_wrong_request_type(self):
        mock_request = rf.post('/api/demographic/delete?session_id=' + str(self.session_id))
        response = demographic_delete(mock_request)

        self.assertTrue('"error_id": 201' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.get('/api/demographic/delete')
        response = demographic_delete(mock_request)

        self.assertTrue('"error_id": 200' in response.content.decode('utf-8'))

    def test_demographic_object_does_not_exist(self):
        self.test_demographic.delete()
        response = demographic_delete(self.demographic_delete_request)

        self.assertTrue('"error_id": 206' in response.content.decode('utf-8'))


class DemographicSelectTests(TestCase):

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

        test_gender = GenderLookup.objects.create(name='Test Gender')
        test_gender.save()

        test_grade_year = GradeYearLookup.objects.create(name='Test Grade Year')
        test_grade_year.save()

        test_ethnicity = EthnicityLookup.objects.create(name='Test Ethnicity')
        test_ethnicity.save()

        test_race = RaceLookup.objects.create(name='Test Race')
        test_race.save()

        self.test_demographic = Demographic.objects.create(student=self.new_student, age=18, gender=test_gender,
                                                           grade_year=test_grade_year, race=test_race,
                                                           ethnicity=test_ethnicity)
        self.test_demographic.save()

        self.demographic_select_request = rf.get('/api/demographic/select?session_id=' + str(self.session_id))

    def test_success_status(self):
        response = demographic_select(self.demographic_select_request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_returns_demographic_information(self):
        response = demographic_select(self.demographic_select_request)

        self.assertTrue('"data"' in response.content.decode('utf-8'))
        self.assertTrue('"id"' in response.content.decode('utf-8'))
        self.assertTrue('"student"' in response.content.decode('utf-8'))
        self.assertTrue('"age"' in response.content.decode('utf-8'))
        self.assertTrue('"race"' in response.content.decode('utf-8'))
        self.assertTrue('"gender"' in response.content.decode('utf-8'))
        self.assertTrue('"grade_year"' in response.content.decode('utf-8'))
        self.assertTrue('"ethnicity"' in response.content.decode('utf-8'))
        self.assertTrue('"major"' in response.content.decode('utf-8'))

    def test_wrong_request_type(self):
        mock_request = rf.post('/api/demographic/select?session_id=' + str(self.session_id))
        response = demographic_select(mock_request)

        self.assertTrue('"error_id": 201' in response.content.decode('utf-8'))

    def test_no_logged_in_user(self):
        mock_request = rf.get('/api/demographic/select')
        response = demographic_select(mock_request)

        self.assertTrue('"error_id": 200' in response.content.decode('utf-8'))

    def test_demographic_object_does_not_exist(self):
        self.test_demographic.delete()
        response = demographic_select(self.demographic_select_request)

        self.assertTrue('"error_id": 206' in response.content.decode('utf-8'))


class DemographicFormTests(TestCase):

    def setUp(self):
        test_gender = GenderLookup.objects.create(name='Test Gender')
        test_gender.save()

        test_grade_year = GradeYearLookup.objects.create(name='Test Grade Year')
        test_grade_year.save()

        test_ethnicity = EthnicityLookup.objects.create(name='Test Ethnicity')
        test_ethnicity.save()

        test_race = RaceLookup.objects.create(name='Test Race')
        test_race.save()

        self.request = rf.get('/api/demographic/form/')

    def test_success_status(self):
        response = demographic_form(self.request)

        self.assertTrue('"status": "success"' in response.content.decode('utf-8'))

    def test_correct_data_returned(self):
        response = demographic_form(self.request)

        self.assertTrue('"data"' in response.content.decode('utf-8'))
        self.assertTrue('"genders"' in response.content.decode('utf-8'))
        self.assertTrue('"grade_years"' in response.content.decode('utf-8'))
        self.assertTrue('"ethnicities"' in response.content.decode('utf-8'))
        self.assertTrue('"races"' in response.content.decode('utf-8'))

    def test_wrong_request_type(self):
        mock_request = rf.post('/api/demographic/form/')
        response = demographic_form(mock_request)

        self.assertTrue('"error_id": 201' in response.content.decode('utf-8'))