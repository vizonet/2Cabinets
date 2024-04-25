from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from app.models import Profile, Offer, Order


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'Password'}))


class ProfileForm(ModelForm):
    """ Класс модельной формы профиля пользователя. """

    userName = forms.CharField(label='Псевдоним', max_length=50,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ('photo', 'userName', 'phoneNumber', 'gender', 'city')   # '__all__'
        # exclude = ('user', 'rate', 'dateReg', 'specializations')

        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),

            # виджет не работает с extra-полем, требуется его явное определение при создании поля
            # 'userName': forms.TextInput(attrs={'class': 'form-control'}),

            'phoneNumber': forms.TextInput(attrs={'class': 'form-control'}),
        }


class OfferForm(ModelForm):
    """ Класс модельной формы заказа. """
    class Meta:
        model = Offer
        fields = ('image', 'title', 'description', 'category', 'processPeriod', 'cost')   # '__all__'
        # exclude = ('user', 'created', 'updated')

        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'processPeriod': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'step': "1", 'class': 'form-control'}),
        }


class OrderForm(ModelForm):
    """ Класс модельной формы заказа. """
    class Meta:
        model = Order
        fields = ('description',)

        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
