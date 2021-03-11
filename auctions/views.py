from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import User, AuctionList, Category, Watchlist, Bids, Comments
from .forms import CreateForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionList.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories_view(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


@login_required(login_url='auctions/login.html')
def create_view(request):
    if request.method == 'POST':
        create_form = CreateForm(request.POST)

        if create_form.is_valid():
            usr = create_form.save(commit=False)
            usr.author = request.user
            usr.save()

            return redirect('index')

    else:
        create_form = CreateForm()
        return render(request, "auctions/create.html", {'form': create_form})


def listing_view(request, product_id):

    item_to_add = get_object_or_404(AuctionList, pk=product_id)
    comment_posts = Comments.objects.filter(product=product_id) or None
    current_product = AuctionList.objects.get(pk=product_id)

    in_watchlist = False

    in_watchlist = True if (request.user.is_authenticated and Watchlist.objects.filter(user=request.user, product=product_id).exists()) else False
        

    owner = True if request.user == current_product.author else False
    #print("OWNER", owner)
    
    if request.method == "POST" and request.POST.get("add_watchlist") == "add":
        #print(item_to_add)
        if Watchlist.objects.filter(user=request.user, product=product_id).exists():
            return render(request, "auctions/product.html", {
                "product": AuctionList.objects.get(id=product_id),
                "in_watchlist": True,
                "comment_posts": comment_posts,
                "owner": owner
            })
            #print("exists")

        else:
            """ADD THE ITEM """
            user_list, created = Watchlist.objects.get_or_create(user=request.user)
            user_list.product.add(item_to_add)
            #print("does not exist, adding")
        
        return render(request, "auctions/product.html", {
            "product": AuctionList.objects.get(id=product_id),
            "in_watchlist": True,
            "comment_posts": comment_posts,
            "owner": owner
        })

    elif request.method == "POST" and request.POST.get("add_watchlist") == "remove":
        # REMOVE THE ITEM
        user_list, created = Watchlist.objects.get_or_create(user=request.user)
        user_list.product.remove(item_to_add)
        in_watchlist = False

        return render(request, "auctions/product.html", {
                "product": AuctionList.objects.get(id=product_id),
                "in_watchlist": in_watchlist,
                "comment_posts": comment_posts,
                "owner": owner
        })

    elif request.method == "GET" and request.user.is_authenticated and current_product.active == True:
        if Watchlist.objects.filter(user=request.user, product=product_id).exists():
            in_watchlist = True
            return render(request, "auctions/product.html", {
                "product": AuctionList.objects.get(id=product_id),
                "in_watchlist": in_watchlist,
                "comment_posts": comment_posts,
                "owner": owner
                })

        else:
            in_watchlist = False
            return render(request, "auctions/product.html", {
                    "product": AuctionList.objects.get(id=product_id),
                    "in_watchlist": in_watchlist,
                    "comment_posts": comment_posts,
                    "owner": owner
                    })           

    #BIDDING
    
    elif request.method == "POST" and request.POST.get("bid"):
        user_bid = float(request.POST.get("bid"))
        current_price = current_product.price
        current_winner = current_product.winner

        if (user_bid > current_price and current_winner != request.user) or (user_bid == current_price and current_winner is None):

            #print("OK", user_bid, current_price)
            current_product.price = user_bid
            current_product.winner = request.user
            current_product.save()
            success = "Done!"
            message = None
            new_bid_entry = Bids.objects.create(product=current_product, user=request.user, bid=user_bid)
            new_bid_entry.save()

        

        elif current_winner == request.user:
            message = "Your bid is currently the highest one."
            success = None

        else:
            message = "Bid must be greater than current winning bid."
            success = None

    
        return render(request, "auctions/product.html", {
                "product": AuctionList.objects.get(id=product_id),
                "in_watchlist": in_watchlist,
                "comment_posts": comment_posts,
                "message": message,
                "success": success,
                "owner": owner
                })

    elif request.method == "POST" and request.POST.get("submit_comment"):
        #print("POST COMMENT", request.POST.get("comment_textarea"))
        comment_textarea = request.POST.get("comment_textarea")
        new_comment = Comments.objects.create(product = current_product, commenter=request.user, comment=comment_textarea)
        new_comment.save()
        comment_posts = Comments.objects.filter(product=product_id) or None

        return render(request, "auctions/product.html", {
                    "product": AuctionList.objects.get(id=product_id),
                    "in_watchlist": in_watchlist, 
                    "comment_posts": comment_posts,
                    "owner": owner
                    })        


    elif request.method == "GET" and request.user == current_product.winner and current_product.active == False:
        print("WIN!")
        message = None
        success = "Congrats! You won this Auction!"
        return render(request, "auctions/product.html", {
                "product": AuctionList.objects.get(id=product_id),
                "in_watchlist": in_watchlist,
                "comment_posts": comment_posts,
                "message": message,
                "success": success,
                "owner": owner
                })


    #else scenarios:
    else:
        return render(request, "auctions/product.html", {
                    "product": AuctionList.objects.get(id=product_id),
                    "in_watchlist": in_watchlist, 
                    "comment_posts": comment_posts,
                    "owner": owner
                    })        

def close_view(request, product_id):
    current_product = AuctionList.objects.get(pk=product_id)
    current_product.active = False
    current_product.save()



    return render(request, "auctions/close.html", {
        "product": AuctionList.objects.get(id=product_id)
    })


def category_listing_view(request, category_name):
    #print("NAME", category_name)
    current_category = Category.objects.get(category_name=category_name)
    category_products = AuctionList.objects.filter(category=current_category)
    
    return render(request, "auctions/category.html", {
        "listings": category_products
    })

def watchlist_view(request):
    watchlist_items = Watchlist.objects.get(user=request.user).product.all()
    print(watchlist_items)
    return render(request, "auctions/watchlist.html", {
        "listings": watchlist_items
    })