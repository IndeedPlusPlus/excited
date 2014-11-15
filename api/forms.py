from django import forms
from common.models import User, Item, UserItem
from django.contrib.auth.hashers import make_password, check_password


class RegisterForm(forms.Form):
    email = forms.EmailField(max_length=255)
    nickname = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    passwordRepeat = forms.CharField(max_length=255)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        if cleaned_data.get('password') != cleaned_data.get('passwordRepeat'):
            self.add_error('passwordRepeat', 'Password not match.')
        if User.objects.filter(email=cleaned_data.get('email')):
            self.add_error('email', 'Email already taken.')
        return cleaned_data

    def register(self, request):
        if self.is_valid():
            user = User()
            cleaned_data = self.clean()
            (user.email, user.nickname, user.password_hash) = (
                cleaned_data.get('email'), cleaned_data.get('nickname'), make_password(cleaned_data.get('password')))
            user.save()
            request.session['user_id'] = user.id
            return user


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=255)
    password = forms.CharField(max_length=255)
    user = None

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        try:
            self.user = self.user or User.objects.get(email=cleaned_data.get('email'))
        except User.DoesNotExist:
            self.add_error('email', 'You have not yet registered.')
            return cleaned_data
        if not check_password(cleaned_data.get('password'), self.user.password_hash):
            self.add_error('password', 'Invalid password.')
        return cleaned_data

    def login(self, request):
        if self.is_valid():
            request.session['user_id'] = self.user.id
        return self.user


class CreateItemForm(forms.Form):
    title = forms.CharField(max_length=65536)
    content = forms.CharField(max_length=65536)

    def save(self, user):
        cleaned_data = self.clean()
        item = Item()
        item.title = cleaned_data.get('title')
        item.content = cleaned_data.get('content')
        item.save()
        user_item = UserItem()
        user_item.item_id = item.id
        user_item.owner_id = user.id
        user_item.save()