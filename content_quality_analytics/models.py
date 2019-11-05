import json

from django.db import models


class Module(models.Model):
    uid = models.CharField(max_length=255)
    mod_name = models.CharField(max_length=255)
    mod_type = models.CharField(max_length=255)

    def __str__(self):
        return json.dumps({'uid': self.uid, 'mod_name': self.mod_name, 'mod_type': self.mod_type})


class Session(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    active = models.BooleanField()

    def __str__(self):
        return json.dumps({'id': self.id, 'active': self.active})


class File(models.Model):
    uid = models.CharField(max_length=255)
    src = models.CharField(max_length=255)

    def __str__(self):
        return json.dumps({'uid': self.uid, 'src': self.src})


class Scale(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=255)
    attr = models.CharField(max_length=255)

    def __str__(self):
        return json.dumps({'name': self.name, 'type': self.type, 'attr': self.attr})


class Indicator(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=255)
    questions = models.CharField(max_length=255)
    show = models.BooleanField()

    def __str__(self):
        return json.dumps({'name': self.name, 'type': self.type, 'questions': self.questions, 'show': self.show})