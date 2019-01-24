from django.db import models
from django.contrib.auth.models import User
import uuid

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
    id = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    age = models.IntegerField()
    gender = models.ForeignKey(GenderLookup, on_delete=models.CASCADE)
    grade_year = models.ForeignKey(GradeYearLookup, on_delete=models.CASCADE)
    ethnicity = models.ForeignKey(EthnicityLookup, on_delete=models.CASCADE)
    race = models.ForeignKey(RaceLookup, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    x = models.FloatField()
    y = models.FloatField()

    def __str__(self):
        return str(self.id) + ' (' + str(self.x) + ', ' + str(self.y) + ')'
