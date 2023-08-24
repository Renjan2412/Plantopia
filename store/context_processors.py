from .models import Wishlist

def wishlist_count(request) :
    item_count = 0

    if 'admin' in request.path :
        return {}
    
    else :
        if request.user.is_authenticated :
            wishlist_items = Wishlist.objects.all().filter(user=request.user)
            item_count = wishlist_items.count()

    return dict(wishlist_count=item_count)        