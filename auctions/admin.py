from django.contrib import admin
from .models import AuctionList, Category, Watchlist, Bids, Comments

# Register your models here.
admin.site.register(Category)
admin.site.register(AuctionList)
admin.site.register(Watchlist)
admin.site.register(Bids)
admin.site.register(Comments)
