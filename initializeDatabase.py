from api.models import GenderLookup, GradeYearLookup, EthnicityLookup, RaceLookup, Student, Demographic
from django.contrib.auth.models import User, Group

# Genders
genders = ['Male', 'Female', 'Other', 'Prefer not to say']
for gender_name in genders:
    new_gender = GenderLookup.objects.create(name=gender_name)
    new_gender.save()

# Grade Year
grade_years = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Super Senior', 'Graduate', 'Other', 'Prefer not to say']
for grade_year in grade_years:
    new_grade_year = GradeYearLookup.objects.create(name=grade_year)
    new_grade_year.save()

# Race
races = ['American Indian or Alaska Native', 'Asian', 'Black or African American',
         'Native Hawaiian or Other Pacific Islander', 'White', 'Other', 'Prefer not to say']
for race in races:
    new_race = RaceLookup.objects.create(name=race)
    new_race.save()

# Ethnicity
ethnicities = ['Hispanic or Latino', 'Not Hispanic or Latino', 'Other', 'Prefer not to say']
for ethnicity in ethnicities:
    new_ethnicity = EthnicityLookup.objects.create(name=ethnicity)
    new_ethnicity.save()

print('Demographic Lookups created!')

# Groups
groups = ['Students', 'Professors', 'Administrator']
for group in groups:
    new_group = Group.objects.create(name=group)
    new_group.save()

print('Groups created!')

# Default Admin
default_admin = User.objects.create(username='BSU_Admin', email="bklawson@bsu.edu", first_name='Admin', last_name='Admin')
default_admin.save()
default_admin.set_password('ICBA2019!@#$')
default_admin.is_staff = True
default_admin.is_superuser = True
default_admin.save()

print('Default admin created!')

# Test User
test_user = User.objects.create(username='test_user', email='test@test.com', first_name='test', last_name='test')
test_user.save()
test_user.set_password('test1234')
test_user.save()

print('Test user created!')

test_student = Student.objects.create(user=test_user)
test_student.save()

print('Test student created!')

test_demo = Demographic.objects.create(student=test_student,
                                       age=18,
                                       gender=GenderLookup.objects.get(id=1),
                                       grade_year=GradeYearLookup.objects.get(id=1),
                                       ethnicity=EthnicityLookup.objects.get(id=1),
                                       race=RaceLookup.objects.get(id=1),
                                       major='Test Major'
                                       )

print('Test Demographic object created!')

test_user.groups.add(Group.objects.get(name='Students'))
test_user.save()

print('Test User added to "Students" group!')

print('Database is ready to go!')
