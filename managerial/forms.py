"""
managerial/forms.py — Staff Account Management Forms for Desaint Stationeries
Enables the CEO to create and modify staff accounts with assigned Desaint RBAC groups.
"""
from django import forms
from django.contrib.auth.models import User, Group
from core.roles import ALL_ROLES, ROLE_CASHIER, ROLE_CEO, get_user_role


class StaffUserCreateForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[(r, r) for r in ALL_ROLES],
        initial=ROLE_CASHIER,
        widget=forms.Select(attrs={'class': 'form-select font-mono'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control font-mono', 'placeholder': 'Enter temporary password'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control font-mono', 'placeholder': 'Confirm temporary password'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control font-mono', 'placeholder': 'e.g. kofi_cashier'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control font-mono', 'placeholder': 'staff@desaintstationeries.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True
        role = self.cleaned_data['role']
        if role == ROLE_CEO:
            user.is_superuser = True
        if commit:
            user.save()
            for r in ALL_ROLES:
                g, _ = Group.objects.get_or_create(name=r)
                if r == role:
                    user.groups.add(g)
                else:
                    user.groups.remove(g)
        return user


class StaffUserEditForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[(r, r) for r in ALL_ROLES],
        widget=forms.Select(attrs={'class': 'form-select font-mono'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control font-mono', 'placeholder': 'Leave blank to keep current password'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control font-mono'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control font-mono'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            current_role = get_user_role(self.instance)
            if current_role in ALL_ROLES:
                self.fields['role'].initial = current_role

    def save(self, commit=True):
        user = super().save(commit=False)
        new_pwd = self.cleaned_data.get('new_password')
        if new_pwd:
            user.set_password(new_pwd)
        role = self.cleaned_data.get('role')
        if role == ROLE_CEO:
            user.is_superuser = True
        else:
            user.is_superuser = False
        if commit:
            user.save()
            for r in ALL_ROLES:
                g, _ = Group.objects.get_or_create(name=r)
                if r == role:
                    user.groups.add(g)
                else:
                    user.groups.remove(g)
        return user
