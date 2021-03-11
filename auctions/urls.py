from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories_view, name="categories"),
    path("category/<str:category_name>", views.category_listing_view, name="category_list"),
    path("create", views.create_view, name="create"),
    path("listings/<int:product_id>/", views.listing_view, name="listing"),
    path("close/<int:product_id>/", views.close_view, name="close"),
    path("watchlist", views.watchlist_view, name="watchlist"),

    
]
