from django.db import models
from django.contrib.auth.models import User
import uuid

# lets us explicitly set upload path and filename
# cari tau gimana cara kerja upload to ini pakek library pillow
def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)

class ProductModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    image_url = models.ImageField(upload_to=upload_to, blank=True, null=True)
    price = models.IntegerField()
    created_by = models.CharField(max_length=200)
    created_date = models.DateField()
    modified_date = models.DateField()
    star_review = models.IntegerField(default=0)

    class Meta:
        def __str__(self) -> str:
            return self.name
        
class CartModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    created_date = models.DateField()
    total_order = models.IntegerField()

    class Meta:
        def __str__(self) -> str:
            return self.created_date

class PurchasingDetailModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    total_price = models.IntegerField()
    created_date = models.DateField()
    modified_date = models.DateField()

    class Meta:
        def __str__(self) -> str:
            return self.id

class PurchasingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purchasing_detail = models.ForeignKey(PurchasingDetailModel, on_delete=models.CASCADE)
    created_date = models.DateField()
    modified_date = models.DateField()

    class Meta:
        def __str__(self) -> str:
            return self.id
        

