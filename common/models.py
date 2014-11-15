from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(max_length=255)
    nickname = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)


class Item(models.Model):
    id = models.BigIntegerField(primary_key=True)
    owner = models.IntegerField(db_index=True)
    title = models.TextField(max_length=65576)
    content = models.TextField(max_length=65576)


