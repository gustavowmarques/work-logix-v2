from django import forms
from .models import CustomUser, Company, Client
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

class CompanyCreationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'email', 'phone', 'website', 'is_contractor', 'is_property_manager', 'is_client']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

class ClientCreationForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'company', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit choices to only property managers
        self.fields['company'].queryset = Company.objects.filter(is_property_manager=True)

        # Tweak widget sizes
        self.fields['address'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        self.fields['notes'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})