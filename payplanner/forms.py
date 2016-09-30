#Forms.py
# Created By: Matt Agresta
# Created On: 9/05/2016
# Holds classes for each django form
#-----------------------------------------------------------#
#Set up Enviroment
from django import forms
from .models import Items, BudgetData, Categories
from django.contrib.admin import widgets
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

#Custom registration form
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
#Edit form to add/edit Expenses and Bills
class ExpensesForm(forms.ModelForm):
    class Meta:
        model = Items
        exclude = ('skiplst',)
        widgets = {'user': forms.HiddenInput(),
                   'itemType': forms.HiddenInput(),
                   'itemName': forms.TextInput(attrs={'class':'form-control',}),
                   'category': forms.Select(attrs={'class':'form-control',}),
                   'itemAmount': forms.NumberInput(attrs={'class':'form-control',}),
                   'payCycle': forms.Select(attrs={'class':'form-control',}),
                   'itemNote': forms.TextInput(attrs={'class':'form-control',}),
                   'nextDueDate': forms.DateInput(attrs={'name': 'date',
                                                         'class':'form-control'}),
                   'endDate': forms.DateInput(attrs={'name': 'date',
                                                     'class':'form-control'})}

#Edit form to add/edit Income Sources
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Items
        exclude = ('category','skiplst')
        widgets = {'user': forms.HiddenInput(),
                   'itemType': forms.HiddenInput(),
                   'itemName': forms.TextInput(attrs={'class':'form-control',}),
                   'itemAmount': forms.NumberInput(attrs={'class':'form-control',}),
                   'payCycle': forms.Select(attrs={'class':'form-control',}),
                   'itemNote': forms.TextInput(attrs={'class':'form-control',}),
                   'nextDueDate': forms.DateInput(attrs={'name': 'date',
                                                         'class':'form-control'}),
                   'endDate': forms.DateInput(attrs={'name': 'date',
                                                     'class':'form-control'})}

class EditForm(forms.ModelForm):
    class Meta:
        model = BudgetData
        exclude = ('effectiveDate',)
        widgets = {'parentItem':forms.HiddenInput()}
        
