from django.forms import ModelForm

from api.models import Class, Survey, SurveyQuestion, ClassEnrollment, Student


class ClassForm(ModelForm):
    class Meta:
        model = Class
        fields = '__all__'
        exclude = ['id', 'admin']


class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = '__all__'
        exclude = ['id', 'admin']

    def __init__(self, admin_id, *args, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.fields['associated_class'].queryset = Class.objects.filter(admin_id=admin_id)


class SurveyQuestionForm(ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = '__all__'
        exclude = ['id']


class ClassEnrollmentForm(ModelForm):
    class Meta:
        model = ClassEnrollment
        fields = '__all__'
        exclude = ['id', 'admin']


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['id', 'admin']

