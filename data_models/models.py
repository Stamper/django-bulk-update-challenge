from django.db import models


class DataModel(models.Model):
    text = models.TextField(max_length=100)
    description = models.TextField(max_length=200)
