from django.db import models
# Create your models here.
from django.utils.timezone import now

from sacco_manager.models import StageController, Sacco, Route


class FareUpdate(models.Model):
    sacco=models.ForeignKey(Sacco,on_delete=models.CASCADE)
    route=models.ForeignKey(Route,on_delete=models.CASCADE)
    amount=models.DecimalField(decimal_places=2,max_digits=10,blank=False,null=False)
    stagecontroller=models.ForeignKey(StageController,on_delete=models.CASCADE)
    created=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='ride_fare'


