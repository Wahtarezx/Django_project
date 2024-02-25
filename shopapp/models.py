from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


def poduct_preview_directory_path(instance: 'Product', filename: str) -> str:
    return 'products/product_{pk}/preview/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно купить в интернет магазине.

    Заказы тут:model:`shopapp.Order`
    """
    class Meta:
        ordering = ['name', 'price']
        # verbose_name_plural = 'products'

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to='')
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('shopapp:product-detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return f'Product (pk={self.pk}, name={self.name!r})'


def product_image_directory_path(instance: 'ProductImage', filename: str) -> str:
    return 'products/product_{pk}/image/{filename}'.format(
        pk=instance.product.pk, filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_directory_path)
    description = models.TextField(max_length=200, null=False, blank=True)


class Order(models.Model):
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders')
    receipt = models.FileField(null=True, upload_to='orders/receipt/')
