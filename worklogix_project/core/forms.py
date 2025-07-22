from django import forms
from django.forms import CheckboxInput, Textarea, DateInput
from django.contrib.auth.forms import UserCreationForm

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
# Shared Styling Base
# ===============================================================
class StyledModelForm(forms.ModelForm):
    """
    Base form class that applies Bootstrap 5 styling to all fields.
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


# ===============================================================
# Company Form
# ===============================================================
class CompanyCreationForm(StyledModelForm):
    class Meta:
        model = Company
        fields = [
            'name',
            'address',
            'email',
            'phone',
            'website',
            'is_contractor',
            'is_property_manager',
            'is_client',
        ]


# ===============================================================
# Client Form
# ===============================================================
class ClientCreationForm(StyledModelForm):
    # These fields are for unit generation & address prefilling
    default_eircode = forms.CharField(
        label="Shared Eircode (for unit address pre-fill)",
        max_length=10,
        required=False
    )
    num_apartments = forms.IntegerField(min_value=0, initial=0, label="Number of Apartments")
    num_duplexes = forms.IntegerField(min_value=0, initial=0, label="Number of Duplexes")
    num_houses = forms.IntegerField(min_value=0, initial=0, label="Number of Houses")
    num_commercial_units = forms.IntegerField(min_value=0, initial=0, label="Number of Commercial Units")

    
    unit_contact_name = forms.CharField(
        label="Default Contact Name for Units",
        max_length=100,
        required=False
    )
    unit_contact_number = forms.CharField(
        label="Default Contact Number for Units",
        max_length=20,
        required=False
    )
    unit_contact_email = forms.EmailField(
        label="Default Contact Email for Units",
        required=False
    )

    class Meta:
        model = Client
        fields = ['name', 'address', 'company', 'notes']  # Do NOT include the extra form-only fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(is_property_manager=True)



# ===============================================================
# Work Order Form
# ===============================================================
class WorkOrderForm(forms.ModelForm):
    """
    Used by Admins or Property Managers to create Work Orders.
    Filters contractors based on business type.
    """
    class Meta:
        model = WorkOrder
        fields = [
            'title',
            'description',
            'priority',
            'business_type',
            'client',
            'unit',
            'preferred_contractor',
            'second_contractor',
            'due_date',
            'attachment',
        ]
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            'due_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['unit'].queryset = Unit.objects.none()  # No units until client selected
        self.fields['client'].queryset = Client.objects.all()
        self.fields['business_type'].queryset = BusinessType.objects.all()
        self.fields['preferred_contractor'].queryset = Company.objects.none()
        self.fields['second_contractor'].queryset = Company.objects.none()

        for field_name, field in self.fields.items():
            if isinstance(field.widget, CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Pre-populate units if client selected (via POST or instance)
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['unit'].queryset = Unit.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                self.fields['unit'].queryset = Unit.objects.none()
        elif self.instance.pk and self.instance.client:
            self.fields['unit'].queryset = Unit.objects.filter(client=self.instance.client)


# ===============================================================
# Unit Forms
# ===============================================================
class UnitCreationForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'client']


class UnitGroupCreationForm(forms.ModelForm):
    class Meta:
        model = UnitGroup
        fields = ['client', 'num_apartments', 'num_duplexes', 'num_houses', 'num_commercial_units']


UNIT_TYPES = [
    ('apartment', 'Apartment'),
    ('duplex', 'Duplex'),
    ('house', 'House'),
    ('commercial', 'Commercial Unit'),
]

class UnitForm(forms.Form):
    unit_number = forms.CharField(max_length=20)
    unit_type = forms.ChoiceField(choices=UNIT_TYPES)
    unit_contact_name = forms.CharField(max_length=100)
    unit_contact_number = forms.CharField(max_length=20)
    unit_contact_email = forms.EmailField()
    eircode = forms.CharField(max_length=10)
    street = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    county = forms.CharField(max_length=100, required=False)

