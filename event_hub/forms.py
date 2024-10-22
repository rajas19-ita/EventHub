from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import MyUser, Event, Tag


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'id': 'email',
            }
        )
    )


class SignUpForm(UserCreationForm):
    usable_password = None

    class Meta:
        model = MyUser
        fields = ['name', 'username', 'email']


class UserUpdateForm(forms.ModelForm):
    bio = forms.CharField(
        max_length=300,
        widget=forms.Textarea,
        required=False
    )

    class Meta:
        model = MyUser
        fields = ['avatar', 'username', 'name', 'bio']


class EventCreateForm(forms.ModelForm):
    short_description = forms.CharField(
        max_length=50,
        required=True,
        label='Event Identifier',
        help_text="A short, memorable description for your event (max 50 characters)."
    )

    datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local'
            }
        ),
        required=True
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Event
        fields = '__all__'
        exclude = ['slug', 'organizer', 'timezone']
