# encoding: utf8
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ExampleModel(models.Model):
    VOTE_CHOICES = (
        ("up", "Up"),
        ("down", "Down"),
    )
    user = models.ForeignKey('auth.user')
    vote = models.CharField(max_length=4, choices=VOTE_CHOICES, blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u"{0} – {1}".format(self.pk, self.user)
