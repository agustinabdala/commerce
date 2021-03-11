from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name


class AuctionList(models.Model):
    title = models.CharField(max_length=64)
    image_url = models.CharField(max_length=1024)
    description = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(blank=True, null=True, default=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="author")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name="winner")

    def __str__(self):
        return self.title


class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(AuctionList, default=None, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return "{} has bid {} for {}".format(self.user, self.bid, self.product.title)
    

class Comments(models.Model):
    product = models.ForeignKey(AuctionList, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Comments from {} for product {}".format(self.commenter, self.product.title)


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(AuctionList, related_name="watchlist_products")
    class Meta:
        ordering = ['user']

        def __str__(self):
            return self.user
    
    def __str__(self):
       return "WatchList from: {}".format(self.user)