from django.db import models

# Create your models here.
class Projeto(models.Model):
    nomeProjeto = models.CharField(max_length=255, null=True)
    idProjeto = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.nomeProjeto