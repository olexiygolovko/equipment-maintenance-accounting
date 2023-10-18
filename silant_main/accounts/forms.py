from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm

class UpdateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'groups', 'is_superuser', 'is_staff', 'is_active')
        widgets = {'groups': forms.SelectMultiple,}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].help_text='Obligatory field. Enter your name or company name'
        self.fields['first_name'].required=True
        self.fields['username'].label='Login'
        self.fields['groups'].help_text='The group to which this user belongs. The user will receive everything' \
                                        'rights, defender in the group. You can make subtle transformations of the rights of the group itself ' \
                                        'in the administrative part of the site (/admin).'
        self.fields['groups'].label='Role (group)'

    def clean_groups(self):
        groups = self.cleaned_data['groups']
        if len(groups) > 1:
            raise forms.ValidationError(f"Select no more than 1 item")
        return groups


class CreateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'email', 'groups', 'is_superuser', 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].help_text='Obligatory field. Enter your name or company name'
        self.fields['first_name'].required=True
        self.fields['username'].label='Логин'
        self.fields['groups'].help_text='The group to which this user belongs. Please select only '\
                                         'one of the groups. The user will receive all rights specified in the group. Thin '\
                                         'you can set up the rights of the group itself in the administrative part of the site' \
                                        '(/admin).'
        self.fields['groups'].label='Role (group)'
        self.fields['groups'].required=True

