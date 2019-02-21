from api.models import GenderLookup, GradeYearLookup, EthnicityLookup, RaceLookup
from django.contrib.auth.models import User

# Default Admin
default_admin = User.objects.create(username='BSU_Admin', email="bklawson@bsu.edu", first_name='Admin', last_name='Admin')
default_admin.set_password('ICBA2019!@#$')
default_admin.is_staff = True
default_admin.is_superuser = True
default_admin.save()

print('Default admin created!')

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
