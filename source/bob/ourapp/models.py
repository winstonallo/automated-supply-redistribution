from django.db import models

class Item(models.Model):
    id = models.AutoField(primary_key=True)

class Store(models.Model):
    id = models.AutoField(primary_key=True)
    x_coordinate = models.FloatField(null=True)
    y_coordinate = models.FloatField(null=True)
    federal_state = models.CharField(max_length=50, null=True)
    warehouse = models.CharField(max_length=50, null=True)
    storage_area = models.FloatField(null=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    demand = models.IntegerField(default=0)
    minimum_required = models.IntegerField(default=0)

    class Meta:
        unique_together = ('store', 'item')

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    source_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='source_store')
    destination_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='destination_store')
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.item} from {self.source_store} to {self.destination_store}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.item} x{self.quantity}'