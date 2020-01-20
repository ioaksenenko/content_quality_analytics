import json

from django.db import models
from datetime import datetime as dt


class Module(models.Model):
    uid = models.CharField(max_length=255, default='')
    sdo = models.CharField(max_length=255, default='')
    cid = models.IntegerField(default=-1)
    mid = models.IntegerField(default=-1)
    sec_name = models.CharField(max_length=255, default='')
    mod_name = models.CharField(max_length=255, default='')
    mod_type = models.CharField(max_length=255, default='')

    def __str__(self):
        return json.dumps({
            'uid': self.uid,
            'sdo': self.sdo,
            'cid': self.cid,
            'mid': self.mid,
            'sec_name': self.sec_name,
            'mod_name': self.mod_name,
            'mod_type': self.mod_type
        })


class File(models.Model):
    uid = models.CharField(max_length=255)
    src = models.CharField(max_length=255)

    def __str__(self):
        return json.dumps({'uid': self.uid, 'src': self.src})


class Scale(models.Model):
    identifier = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, default='')
    type = models.CharField(max_length=255, default='')
    attr = models.CharField(max_length=255, default='')

    def __str__(self):
        return json.dumps({
            'identifier': self.identifier,
            'name': self.name,
            'type': self.type,
            'attr': self.attr
        })


class Indicator(models.Model):
    identifier = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, default='')
    type = models.CharField(max_length=255, default='')
    questions = models.CharField(max_length=255, default='')
    show = models.BooleanField(default=True)
    description = models.CharField(max_length=255, default='')

    def __str__(self):
        return json.dumps({
            'identifier': self.identifier,
            'name': self.name,
            'type': self.type,
            'questions': self.questions,
            'show': self.show,
            'description': self.description
        })


class Results(models.Model):
    uid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    context = models.CharField(max_length=255)

    def __str__(self):
        return json.dumps({
            'uid': self.uid,
            'name': self.name,
            'context': self.context,
        })


class Course(models.Model):
    uid = models.CharField(max_length=255, default='')
    identifier = models.IntegerField(default=0)
    moodle = models.CharField(max_length=255, default='')
    rating = models.FloatField(default=0)
    context = models.CharField(max_length=255, default='')
    datetime = models.DateTimeField(default=dt.now())

    def __str__(self):
        return json.dumps({
            'uid': self.uid,
            'identifier': self.identifier,
            'moodle': self.moodle,
            'rating': self.rating,
            'context': self.context,
            'datetime': self.datetime
        })
