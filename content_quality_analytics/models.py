import json

from django.db import models


class Module(models.Model):
    uid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return json.dumps({'uid': self.uid, 'name': self.name})


class Session(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    active = models.BooleanField()

    def __str__(self):
        return json.dumps({'id': self.id, 'active': self.active})