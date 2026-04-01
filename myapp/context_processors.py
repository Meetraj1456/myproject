from .models import User, Add_to_cart, Wishlist, Categories


def current_user(request):
    email = request.session.get('email')
    if not email:
        return {'current_user': None, 'cart_count': 0, 'wishlist_count': 0, 'categories': Categories.objects.all()}

    user = User.objects.filter(email=email).first()

    # Get cart count and wishlist count for logged-in users
    if user:
        cart_count = Add_to_cart.objects.filter(uid=user).count()
        wishlist_count = Wishlist.objects.filter(uid=user).count()
    else:
        cart_count = 0
        wishlist_count = 0

    return {
        'current_user': user, 
        'cart_count': cart_count, 
        'wishlist_count': wishlist_count,
        'categories': Categories.objects.all()
    }
