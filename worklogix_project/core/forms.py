from django import forms
from .models import CustomUser, Company
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for Admins to create users with role and associated company.
    Inherits from Django's built-in UserCreationForm to handle password1 & password2.
    """
    role = forms.ChoiceField(choices=CustomUser._meta.get_field('role').choices)
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'company']

    def clean_company(self):
        """
        Ensure that only Admins can be created without a company assigned.
        All other roles must have a linked company.
        """
        role = self.cleaned_data.get('role')
        company = self.cleaned_data.get('company')

        if role != 'admin' and not company:
            raise forms.ValidationError("Non-admin users must be assigned to a company.")
        return company
