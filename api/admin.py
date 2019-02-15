from django.contrib import admin
from api.models import *

# Register your models here.

admin.site.register(Student)
admin.site.register(Demographic)
admin.site.register(GenderLookup)
admin.site.register(GradeYearLookup)
admin.site.register(EthnicityLookup)
admin.site.register(Position)
admin.site.register(RaceLookup)
admin.site.register(Class)
admin.site.register(ClassEnrollment)
