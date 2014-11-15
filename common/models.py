from common.utils import get_time_milliseconds
from django.db import models


class User(models.Model):
    email = models.EmailField(max_length=255)
    nickname = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)


class Item(models.Model):
    title = models.TextField(max_length=65536)
    content = models.TextField(max_length=65536)
    created_on = models.BigIntegerField(default=get_time_milliseconds, blank=True)


class UserItem(models.Model):
    owner = models.ForeignKey('User')
    item = models.ForeignKey('Item')
    created_on = models.BigIntegerField(default=get_time_milliseconds, blank=True)
    finished_on = models.BigIntegerField(default=0, blank=True)
    finished = models.BooleanField(default=False)

    def finish(self):
        self.finished = True
        self.finished_on = get_time_milliseconds()

    def unfinish(self):
        self.finished = False
        self.finished_on = 0