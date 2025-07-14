from django import forms
from .models import CustomUser, Company, Client, WorkOrder, BusinessType, Unit, UnitGroup
from django.contrib.auth.forms import UserCreationForm

from django.forms import CheckboxInput, Textarea, ModelChoiceField, DateInput

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

class WorkOrderForm(forms.ModelForm):
    """
    Form for Admins or Property Managers to create Work Orders.
    Includes logic to filter contractors by business type.
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

    class WorkOrderForm(forms.ModelForm):
        class Meta:
            model = WorkOrder
            fields = '__all__'  # Or explicitly list fields if preferred

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default to no units shown until a client is selected
        self.fields['unit'].queryset = Unit.objects.none()

        # Apply Bootstrap 5 styling
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Show all clients
        self.fields['client'].queryset = Client.objects.all()

        # Show all business types
        self.fields['business_type'].queryset = BusinessType.objects.all()

        # Preferred and second contractors will be filtered in the view
        self.fields['preferred_contractor'].queryset = Company.objects.none()
        self.fields['second_contractor'].queryset = Company.objects.none()

        # Dynamically filter unit dropdown based on selected client
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['unit'].queryset = Unit.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                self.fields['unit'].queryset = Unit.objects.none()
        elif self.instance.pk and self.instance.client:
            self.fields['unit'].queryset = Unit.objects.filter(client=self.instance.client)


class UnitCreationForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'client']

class UnitGroupCreationForm(forms.ModelForm):
    class Meta:
        model = UnitGroup
        fields = ['client', 'num_apartments', 'num_duplexes', 'num_houses', 'num_commercial_units']
