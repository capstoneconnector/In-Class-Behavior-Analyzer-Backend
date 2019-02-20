from django.db import models
from django.contrib.auth.models import User
import uuid, datetime

# Create your models here.


class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_password_code = models.CharField(max_length=6, null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.id)


class GenderLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return str(self.name)


class GradeYearLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return str(self.name)


class RaceLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class EthnicityLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class Demographic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.ForeignKey(GenderLookup, on_delete=models.CASCADE)
    grade_year = models.ForeignKey(GradeYearLookup, on_delete=models.CASCADE)
    ethnicity = models.ForeignKey(EthnicityLookup, on_delete=models.CASCADE)
    race = models.ForeignKey(RaceLookup, on_delete=models.CASCADE)
    major = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)

    def to_dict(self):
        return {'id': self.id, 'student': self.student.id, 'age': self.age, 'gender': self.gender.id,
                'grade_year': self.grade_year.id, 'ethnicity': self.ethnicity.id, 'race': self.race.id, 'major': self.major}


class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    x = models.FloatField()
    y = models.FloatField()

    def __str__(self):
        return str(self.id) + ' (' + str(self.x) + ', ' + str(self.y) + ')'


class Class(models.Model):
    class Meta:
        verbose_name_plural = "Classes"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    students = models.ManyToManyField(Student, through='ClassEnrollment', through_fields=('class_enrolled', 'student'))
    title = models.CharField(max_length=50)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    SEMESTERS = (
        ('FL', 'Fall'),
        ('SP', 'Spring'),
        ('SM', 'Summer')
    )
    semester = models.CharField(max_length=2, choices=SEMESTERS, default='FL')
    year = models.IntegerField(default=datetime.datetime.now().year)

    def __str__(self):
        return self.title + ' - ' + str(self.admin.username)


class ClassEnrollment(models.Model):
    class Meta:
        verbose_name_plural = "Class Enrollments"
        unique_together = ('student', 'class_enrolled')

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return self.class_enrolled.title + ' - ' + str(self.student.id)
