# encoding: utf8
from django.db import models


class ExampleModel(models.Model):
    VOTE_CHOICES = (
        ("up", "Up"),
        ("down", "Down"),
    )
    user = models.ForeignKey('auth.user')
    vote = models.CharField(max_length=4, choices=VOTE_CHOICES, blank=True)

    def __unicode__(self):
        return u"{0} – {1}".format(self.pk, self.user)
