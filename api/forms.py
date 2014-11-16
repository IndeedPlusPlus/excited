import json
import hashlib

from django import forms
from django.contrib.auth.hashers import make_password, check_password

from common.models import User, Item, UserItem


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
        item.meta = json.dumps({'type': 'todo', 'mail_hash': hashlib.md5(user.email).hexdigest()})
        item.source = user.nickname
        item.save()
        user_item = UserItem()
        user_item.item = item
        user_item.owner_id = user.id
        user_item.save()
        return user_item


class PickItemForm(forms.Form):
    item_id = forms.IntegerField()
    item = None

    def clean(self):
        cleaned_data = super(PickItemForm, self).clean()
        try:
            self.item = Item.objects.get(pk=cleaned_data.get('item_id'))
        except Item.DoesNotExist:
            self.add_error('item_id', 'Item does not exist.')
        return cleaned_data

    def pick(self, user):
        user_item, created = UserItem.objects.get_or_create(
            item_id=self.item.id,
            owner_id=user.id)
        return user_item


class UserItemRelatedForm(forms.Form):
    user_item_id = forms.IntegerField()
    user_item = None
    user = None

    def __init__(self, data, user):
        super(UserItemRelatedForm, self).__init__(data)
        self.user = user

    def clean(self):
        cleaned_data = super(UserItemRelatedForm, self).clean()
        try:
            self.user_item = UserItem.objects.get(pk=cleaned_data.get('user_item_id'))
        except UserItem.DoesNotExist:
            self.add_error('user_item_id', 'User item does not exist.')
        if self.user_item.owner_id != self.user.id:
            self.add_error('user_item_id', 'This user item does not belong to you.')
        return cleaned_data


class DeleteUserItemForm(UserItemRelatedForm):
    def delete(self):
        if self.user_item is not None:
            self.user_item.delete()


class FinishUserItem(UserItemRelatedForm):
    def finish(self):
        if self.user_item is not None:
            self.user_item.finish()
            self.user_item.save()
            return self.user_item


class UnfinishUserItem(UserItemRelatedForm):
    def unfinish(self):
        if self.user_item is not None:
            self.user_item.unfinish()
            self.user_item.save()
            return self.user_item