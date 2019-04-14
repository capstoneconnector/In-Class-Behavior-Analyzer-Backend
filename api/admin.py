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
admin.site.register(Session)
admin.site.register(Survey)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyResponse)
admin.site.register(SurveyInstance)
admin.site.register(SurveyEntryInstance)
admin.site.register(SurveyQuestionInstance)
admin.site.register(SurveyPositionInstance)
