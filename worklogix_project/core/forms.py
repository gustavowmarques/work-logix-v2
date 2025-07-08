from django import forms
from .models import CustomUser, Company, Client
from django.contrib.auth.forms import UserCreationForm

from django.forms import CheckboxInput, Textarea

class StyledModelForm(forms.ModelForm):
    """
    Base form to apply Bootstrap 5 styling. Only applies 'form-control' where appropriate.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget

            # Skip checkboxes – apply checkbox-specific class
            if isinstance(widget, CheckboxInput):
                widget.attrs.update({
                    'class': 'form-check-input',
                })
            elif isinstance(widget, Textarea):
                widget.attrs.update({
                    'class': 'form-control',
                    'rows': 3,
                })
            else:
                widget.attrs.update({
                    'class': 'form-control',
                })

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser._meta.get_field('role').choices)
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'company']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_company(self):
        role = self.cleaned_data.get('role')
        company = self.cleaned_data.get('company')
        if role != 'admin' and not company:
            raise forms.ValidationError("Non-admin users must be assigned to a company.")
        return company


class CompanyCreationForm(StyledModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'email', 'phone', 'website', 'is_contractor', 'is_property_manager', 'is_client']


class ClientCreationForm(StyledModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'company', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(is_property_manager=True)
