from django import forms
from django.contrib.auth.forms import UserCreationForm
from.models import UserProfile

class RegistrationForm(UserCreationForm):
    email=forms.EmailField(required=True)
    phone_number=forms.CharField(max_length=15)
    dob=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender=forms.ChoiceField(choices=[('Male','Male'),('Female','Female'),('Other','Other')])

    class Meta:
        model=UserProfile
        fields=['first_name','last_name','email','phone_number','dob','gender','password1','password2']
from django import forms
from .models import CrimeReport

class CrimeReportForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = '__all__'
