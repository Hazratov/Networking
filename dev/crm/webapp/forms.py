from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Record, Lead, Communication

from django import forms

from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

# - Register/Create a user
class CreateUserForm(UserCreationForm):

    class Meta:

        model = User
        fields = ['username', 'password1', 'password2']

# - Login a user

class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())

# - Create a record
class CreateRecordForm(forms.ModelForm):
    class Meta:

        model = Record
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'province', 'country']

# - Update a record
class UpdateRecordForm(forms.ModelForm):

    class Meta:

        model = Record
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'province', 'country']


# - Create a lead
class CreateLeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['customer', 'status', 'assigned_to', 'note']

# - Create communication
class CreateCommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['customer', 'type', 'note']

    def __init__(self, *args, **kwargs):
        super(CreateCommunicationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



# - Update communication
class UpdateCommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['customer', 'type', 'note']

    def __init__(self, *args, **kwargs):
        super(UpdateCommunicationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UpdateLeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['customer', 'status', 'assigned_to', 'note']

    def __init__(self, *args, **kwargs):
        super(UpdateLeadForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'