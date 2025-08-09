# core/forms.py

from django import forms
from django.forms import CheckboxInput, Textarea, DateInput
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from core.models import (
    CustomUser,
    Company,
    Client,
    WorkOrder,
    BusinessType,
    Unit,
    UnitGroup,
)

# ===============================================================
# Shared Styling Base for Bootstrap 5
# ===============================================================
class StyledModelForm(forms.ModelForm):
    """
    Base form that applies Bootstrap 5 styling to all fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, CheckboxInput):
                widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(widget, Textarea):
                widget.attrs.update({'class': 'form-control', 'rows': 3})
            else:
                widget.attrs.update({'class': 'form-control'})

# ===============================================================
# User Form
# ===============================================================
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
    
class CustomUserEditForm(UserChangeForm):
    role = forms.ChoiceField(choices=CustomUser._meta.get_field('role').choices)
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'company']

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
# ===============================================================
# Company Form
# ===============================================================
class CompanyCreationForm(StyledModelForm):
    """
    Form for creating and editing companies.
    """
    class Meta:
        model = Company
        fields = [
            'name', 'registration_number', 'email', 'telephone',
            'contact_name', 'contact_email', 'address', 'business_type', 'website',
            'is_contractor', 'is_property_manager'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['business_type'].queryset = BusinessType.objects.all().order_by('name')
        self.fields['business_type'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_contractor = cleaned_data.get('is_contractor')
        business_type = cleaned_data.get('business_type')

        if is_contractor and not business_type:
            self.add_error('business_type', 'Business type is required for contractor companies.')

        return cleaned_data

# ===============================================================
# Client Form
# ===============================================================
class ClientCreationForm(StyledModelForm):
    default_eircode = forms.CharField(label="Shared Eircode", max_length=10, required=False)
    num_apartments = forms.IntegerField(min_value=0, initial=0)
    num_duplexes = forms.IntegerField(min_value=0, initial=0)
    num_houses = forms.IntegerField(min_value=0, initial=0)
    num_commercial_units = forms.IntegerField(min_value=0, initial=0)

    unit_contact_name = forms.CharField(max_length=100, required=False)
    unit_contact_number = forms.CharField(max_length=20, required=False)
    unit_contact_email = forms.EmailField(required=False)

    class Meta:
        model = Client
        fields = ['name', 'address', 'company', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(is_property_manager=True)

# ===============================================================
# Unit Generator Form
# ===============================================================
class UnitGeneratorForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all())
    prefix = forms.CharField(max_length=50, initial="Unit")
    start = forms.IntegerField(min_value=1)
    end = forms.IntegerField(min_value=1)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('end') < cleaned_data.get('start'):
            raise forms.ValidationError("End number must be greater than or equal to start number.")

# ===============================================================
# Work Order Form
# ===============================================================
class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = [
            'title', 'description', 'priority', 'business_type', 'client', 'unit',
            'preferred_contractor', 'second_contractor', 'due_date', 'attachment'
        ]
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            'due_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['business_type'].queryset = BusinessType.objects.all()
        self.fields['client'].queryset = Client.objects.all()
        self.fields['unit'].queryset = Unit.objects.none()
        self.fields['preferred_contractor'].queryset = Company.objects.none()
        self.fields['second_contractor'].queryset = Company.objects.none()

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['unit'].queryset = Unit.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.client:
            self.fields['unit'].queryset = Unit.objects.filter(client=self.instance.client)

        if 'business_type' in self.data:
            try:
                bt_id = int(self.data.get('business_type'))
                contractors = Company.objects.filter(is_contractor=True, business_type_id=bt_id)
                self.fields['preferred_contractor'].queryset = contractors
                self.fields['second_contractor'].queryset = contractors
            except (ValueError, TypeError):
                pass

# ===============================================================
# Unit Forms
# ===============================================================
UNIT_TYPES = [
    ('apartment', 'Apartment'),
    ('duplex', 'Duplex'),
    ('house', 'House'),
    ('commercial', 'Commercial Unit'),
]

class UnitCreationForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'client']

class UnitGroupCreationForm(forms.ModelForm):
    class Meta:
        model = UnitGroup
        fields = ['client', 'num_apartments', 'num_duplexes', 'num_houses', 'num_commercial_units']

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            'name', 'unit_type', 'eircode', 'street', 'city', 'county',
            'unit_contact_name', 'unit_contact_email', 'unit_contact_number'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UnitBulkCreateForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), label="Client")
    prefix = forms.CharField(max_length=50, initial="Apt", label="Unit Prefix")
    start_number = forms.IntegerField(min_value=1, initial=1)
    quantity = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
