from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Address(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    project = models.CharField(max_length=255, null=True)
    app = models.CharField(max_length=255, null=True)
    model = models.CharField(max_length=255, null=True)
    cp4 = models.IntegerField()
    cp3 = models.IntegerField()
    postal_code = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    more_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    

class DistrictData(models.Model):
    DD = models.CharField(max_length=255, primary_key=True)
    DESIG = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.DD} - {self.DESIG}"

class CountyData(models.Model):
    DD = models.ForeignKey(DistrictData, on_delete=models.CASCADE)
    CC = models.CharField(max_length=255)
    DESIG = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.CC} - {self.DESIG}"

class CPData(models.Model):
    DD = models.ForeignKey(DistrictData, on_delete=models.CASCADE)
    CC = models.ForeignKey(CountyData, on_delete=models.CASCADE)
    LLLL = models.CharField(max_length=255)
    LOCALIDADE = models.CharField(max_length=255)
    ART_COD = models.CharField(max_length=255)
    ART_TIPO = models.CharField(max_length=255)
    PRI_PREP = models.CharField(max_length=255)
    ART_TITULO = models.CharField(max_length=255)
    SEG_PREP = models.CharField(max_length=255)
    ART_DESIG = models.CharField(max_length=255)
    ART_LOCAL = models.CharField(max_length=255)
    TROÇO = models.CharField(max_length=255)
    PORTA = models.CharField(max_length=255)
    CLIENTE = models.CharField(max_length=255)
    CP4 = models.CharField(max_length=255)
    CP3 = models.CharField(max_length=255)
    CPALF = models.CharField(max_length=255)
