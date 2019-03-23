from django.forms import ModelForm

from api.models import Class, Survey, SurveyQuestion, SurveyResponse


class ClassForm(ModelForm):
    class Meta:
        model = Class
        fields = '__all__'
        exclude = ['admin']


class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = '__all__'
        exclude = ['id', 'admin']


class SurveyQuestionForm(ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = '__all__'
        exclude = ['id']
