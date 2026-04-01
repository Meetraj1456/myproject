from . import views
from django.urls import path


urlpatterns = [
    path('', views.home, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('demo/', views.demo, name='demo'),

    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_cart/<int:id>/', views.remove_cart, name='remove_cart'),
    path('plus/<int:id>/', views.plus, name='plus'),
    path('minus/<int:id>/', views.minus, name='minus'),
    path('update_qty_plus_ajax/<int:id>/', views.update_qty_plus_ajax, name='update_qty_plus_ajax'),
    path('update_qty_minus_ajax/<int:id>/', views.update_qty_minus_ajax, name='update_qty_minus_ajax'),

    path('product_details/<int:id>/',
         views.product_details, name='product_details'),
    path('search/', views.search, name='search'),
    path('category_market/', views.category_market, name='category_market'),
    path('categories/<int:id>/', views.categories, name='categories'),

    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('invoice/<int:order_id>/', views.invoice_pdf, name='invoice_pdf'),
    path('billing/', views.billing, name='billing'),
    path('edit_address/', views.edit_address, name='edit_address'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_wishlist/<int:id>/',
         views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_wishlist/<int:id>/',
         views.remove_wishlist, name='remove_wishlist'),
    
     path('ai/', views.ai_page, name='ai_page'),
     path('ai_chat/', views.ai_chat, name='ai_chat'),

]
