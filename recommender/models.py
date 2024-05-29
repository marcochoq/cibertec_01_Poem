from django.db import models

# Create your models here.
class Poem(models.Model):
    title = models.CharField(max_length=200)
    poet = models.CharField(max_length=100)
    content = models.TextField()
    tags = models.CharField(max_length=200)

    def __str__(self):
        return self.title
