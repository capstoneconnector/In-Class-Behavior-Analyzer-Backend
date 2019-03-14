from django.forms import ModelForm

from api.models import Class


class ClassForm(ModelForm):
    class Meta:
        model = Class
        fields = '__all__'
        exclude = ['admin']