from django.forms import ModelForm
from .models import Demographic, Position


class DemographicForm(ModelForm):
    class Meta:
        model = Demographic
        fields = '__all__'
        exclude = ['id']


class PositionForm(ModelForm):
    class Meta:
        model = Position
        fields = '__all__'
        exclude = ['id', 'timestamp']