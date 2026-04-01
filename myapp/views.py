from .models import User
from .models import *
from django.shortcuts import render, redirect
from django.db.models import Q
import razorpay
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from functools import wraps
from io import BytesIO
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from . models import *

# Create your views here.

# Custom login required decorator for custom User model


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if "email" not in request.session:
            messages.warning(
                request, 'Please login or register to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# Alias for login_required
login_required_custom = login_required


def login_view(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        con = {
            'uid': uid
        }
        return redirect('index')
    else:
        try:
            if request.method == "POST":
                email = request.POST['email']
                password = request.POST['password']

                if not email or not password:
                    messages.error(request, 'Email and password are required.')
                    return render(request, "login.html")

                uid = User.objects.get(email=email)

                if uid.email == email:
                    if uid.password == password:
                        request.session['email'] = uid.email

                        con = {
                            'uid': uid
                        }
                        return redirect('index')
                    else:
                        messages.error(request, 'Invalid password.')
                        return render(request, "login.html")
                else:
                    messages.error(request, 'Email not found.')
                    return render(request, "login.html")
            else:
                return render(request, "login.html")
        except:
            messages.error(request, 'Email not found.')
            return render(request, "login.html")


def signup_view(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone_no = request.POST['phone_no']
        password = request.POST['password']

        if not name or not email or not phone_no or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(
                request, 'This email is already registered. Please log in.')
            return redirect('login')

        if len(password) < 8:
            messages.error(
                request, 'Password must be at least 8 characters long.')
            return render(request, 'signup.html')

        if not re.search(r'[A-Z]', password):
            messages.error(
                request, 'Password must include an uppercase letter.')
            return render(request, 'signup.html')

        if not re.search(r'[a-z]', password):
            messages.error(
                request, 'Password must include a lowercase letter.')
            return render(request, 'signup.html')

        if not re.search(r'\d', password):
            messages.error(request, 'Password must include a number.')
            return render(request, 'signup.html')

        if not re.search(r'[^A-Za-z0-9]', password):
            messages.error(request, 'Password must include a symbol.')
            return render(request, 'signup.html')

        User.objects.create(
            name=name,
            email=email,
            phone_no=phone_no,
            password=password
        )
        messages.success(
            request, 'Account created successfully! Please login.')
        return redirect('login')

    else:
        return render(request, 'signup.html')


def logout_view(request):
    if "email" in request.session:
        del request.session['email']
    
    # Clear all previous messages (like cart messages)
    storage = messages.get_messages(request)
    for message in storage:
        pass  # Iterate through to mark them as used/read
    storage.used = True
    
    # Add logout message
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def home(request):
    # Home page is accessible to everyone
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        pid = Add_product.objects.all()
        con = {
            'uid': uid,
            'pid': pid
        }
        return render(request, 'index.html', con)
    else:
        return render(request, 'index.html')


@login_required
def cart(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        aid = Add_to_cart.objects.filter(uid=uid)

        con = {
            'uid': uid,
            'aid': aid
        }
        return render(request, 'cart.html', con)
    else:
        return render(request, 'cart.html')


@login_required
def add_to_cart(request, id):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        pid = Add_product.objects.get(id=id)

        # Check if product already exists in user's cart
        existing_item = Add_to_cart.objects.filter(uid=uid, pid=pid).first()

        if existing_item:
            # If product already in cart, increase quantity instead of creating duplicate
            existing_item.qty += 1
            existing_item.total_price = existing_item.price * existing_item.qty
            existing_item.save()
            messages.success(request, f'{pid.name} quantity updated in cart.')
        else:
            # Create new cart item
            Add_to_cart.objects.create(
                uid=uid,
                pid=pid,
                name=pid.name,
                price=pid.price,
                qty=1,
                img=pid.img,
                total_price=pid.price
            )
            messages.success(request, f'{pid.name} added to cart.')

        return redirect('cart')
    else:
        return render(request, 'category_market.html')


@login_required
def remove_cart(request, id):
    rid = Add_to_cart.objects.get(id=id).delete()
    return redirect('cart')


@login_required
def plus(request, id):

    pid = Add_to_cart.objects.get(id=id)

    if pid:
        pid.qty = pid.qty + 1
        pid.total_price = pid.qty * pid.price
        pid.save()

    return redirect('cart')


@login_required
def minus(request, id):
    mid = Add_to_cart.objects.get(id=id)

    if mid.qty == 1:
        mid.delete()
        return redirect('cart')
    else:
        if mid:
            mid.qty = mid.qty - 1
            mid.total_price = mid.qty * mid.price
            mid.save()

    return redirect('cart')


@login_required
def update_qty_plus_ajax(request, id):
    """AJAX endpoint to increase quantity in checkout with maximum of 6"""
    try:
        item = Add_to_cart.objects.get(id=id)
        
        # Prevent quantity from going above 6
        if item.qty >= 6:
            return JsonResponse({
                'success': True,
                'qty': 6,
                'total_price': item.total_price,
                'max_qty_reached': True
            })
        
        item.qty += 1
        item.total_price = item.qty * item.price
        item.save()
        
        return JsonResponse({
            'success': True,
            'qty': item.qty,
            'total_price': item.total_price,
            'max_qty_reached': False
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def update_qty_minus_ajax(request, id):
    """AJAX endpoint to decrease quantity in checkout with minimum of 1"""
    try:
        item = Add_to_cart.objects.get(id=id)
        
        # Prevent quantity from going below 1
        if item.qty <= 1:
            return JsonResponse({
                'success': True,
                'qty': 1,
                'total_price': item.total_price,
                'deleted': False,
                'min_qty_reached': True
            })
        else:
            item.qty -= 1
            item.total_price = item.qty * item.price
            item.save()
            
            return JsonResponse({
                'success': True,
                'qty': item.qty,
                'total_price': item.total_price,
                'deleted': False,
                'min_qty_reached': False
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def categories(request, id):
    uid = User.objects.get(email=request.session['email'])

    cid = Categories.objects.all()   # keep sidebar visible
    cmid = Add_product.objects.filter(categories_id=id)

    con = {
        'uid': uid,
        'cid': cid,
        'cmid': cmid
    }
    return render(request, 'category_market.html', con)


@login_required
def category_market(request):
    uid = User.objects.get(email=request.session['email'])

    cid = Categories.objects.all()        # sidebar categories
    cmid = Add_product.objects.all()      # all products

    con = {
        'uid': uid,
        'cid': cid,
        'cmid': cmid
    }
    return render(request, 'category_market.html', con)


@login_required
def search(request):
    query = request.GET.get('q', '')
    response_format = request.GET.get('format', 'html')
    
    # Get user if logged in, otherwise None
    uid = None
    if 'email' in request.session:
        try:
            uid = User.objects.get(email=request.session['email'])
        except User.DoesNotExist:
            uid = None
    
    cid = Categories.objects.all()  # sidebar categories
    
    # Search products by name (case-insensitive) or description
    if query:
        cmid = Add_product.objects.filter(
            Q(name__icontains=query) | Q(desc__icontains=query)
        )
    else:
        cmid = Add_product.objects.all()
    
    # Return JSON if requested
    if response_format == 'json':
        products_data = []
        for product in cmid:
            # Get category name if it exists
            category_name = product.categories_id.name if product.categories_id else 'Products'
            
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'img': product.img.url,
                'desc': product.desc[:100],
                'category': category_name
            })
        return JsonResponse({
            'query': query,
            'products': products_data
        })
    
    con = {
        'uid': uid,
        'cid': cid,
        'cmid': cmid,
        'search_query': query
    }
    return render(request, 'category_market.html', con)


@login_required
def product_details(request, id):
    uid = User.objects.get(email=request.session['email'])

    prid = Add_product.objects.get(id=id)

    con = {
        'uid': uid,
        'prid': prid
    }
    return render(request, 'product_details.html', con)


@login_required
def billing(request):
    uid = User.objects.get(email=request.session['email'])
    
    if request.POST:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        address = request.POST['address']
        country = request.POST['country']
        zip_code = request.POST['zip_code']
        state = request.POST['state']
        selected_address_id = request.POST.get('selected_address_id', '')
        
        # If a previous address was selected without modification, use it directly
        if selected_address_id:
            try:
                addr_obj = Address.objects.get(id=selected_address_id, uid=uid)
                # Check if form was modified from original address
                if (addr_obj.first_name == first_name and 
                    addr_obj.last_name == last_name and 
                    addr_obj.email == email and 
                    addr_obj.address == address and 
                    addr_obj.country == country and 
                    str(addr_obj.zip_code) == zip_code and 
                    addr_obj.state == state):
                    # No modification, use existing address
                    pass
                else:
                    # Form was modified, create new address
                    addr_obj = Address.objects.create(uid=uid,
                                           first_name=first_name,
                                           last_name=last_name,
                                           email=email,
                                           address=address,
                                           country=country,
                                           zip_code=zip_code,
                                           state=state
                                           )
            except Address.DoesNotExist:
                # If address doesn't exist, create new one
                addr_obj = Address.objects.create(uid=uid,
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email,
                                       address=address,
                                       country=country,
                                       zip_code=zip_code,
                                       state=state
                                       )
        else:
            # No address selected, create new one
            addr_obj = Address.objects.create(uid=uid,
                                   first_name=first_name,
                                   last_name=last_name,
                                   email=email,
                                   address=address,
                                   country=country,
                                   zip_code=zip_code,
                                   state=state
                                   )

        # Store address info in session for checkout
        request.session['delivery_address'] = {
            'id': addr_obj.id,
            'first_name': addr_obj.first_name,
            'last_name': addr_obj.last_name,
            'email': addr_obj.email,
            'address': addr_obj.address,
            'country': addr_obj.country,
            'state': addr_obj.state,
            'zip_code': addr_obj.zip_code
        }
        request.session.modified = True

        return redirect('checkout')
    else:
        # Get the last saved address for autofill
        last_address = Address.objects.filter(uid=uid).order_by('-id').first()
        # Get all addresses for selection
        all_addresses = Address.objects.filter(uid=uid).order_by('-id')
        context = {
            'address': last_address,
            'all_addresses': all_addresses
        }
        return render(request, "billing.html", context)


@login_required
def edit_address(request):
    uid = User.objects.get(email=request.session['email'])
    
    if request.POST:
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        country = request.POST.get('country', '')
        zip_code = request.POST.get('zip_code', '')
        state = request.POST.get('state', '')

        Address.objects.create(
            uid=uid,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            country=country,
            zip_code=zip_code,
            state=state
        )
        
        messages.success(request, 'Address updated successfully!')
        return redirect('dashboard')
    else:
        current_address = Address.objects.filter(uid=uid).order_by('-id').first()
        context = {
            'uid': uid,
            'address': current_address
        }
        return render(request, "edit_address.html", context)


@login_required
def checkout(request):
    uid = User.objects.get(email=request.session['email'])
    prod = Add_to_cart.objects.filter(uid=uid)

    if not prod.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    sub_total = 0
    total = 0

    try:
        for i in prod:
            sub_total += i.price * i.qty

        shipping = 0 if sub_total >= 3000 else 50
        total = sub_total + shipping
        amount = total * 100

        client = razorpay.Client(
            auth=('rzp_test_bilBagOBVTi4lE', '77yKq3N9Wul97JVQcjtIVB5z')
        )

        response = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        })

        # Get delivery address from session
        delivery_address = request.session.get('delivery_address', None)

        context = {
            'uid': uid,
            'prod': prod,
            'response': response,
            'total': total,
            'sub_total': sub_total,
            'shipping': shipping,
            'delivery_address': delivery_address
        }

        return render(request, "checkout.html", context)

    except Exception as e:
        print(e)
        return render(request, "checkout.html")


@login_required
def success(request):
    uid = User.objects.get(email=request.session['email'])
    cart_items = Add_to_cart.objects.filter(uid=uid)

    if not cart_items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    sub_total = 0
    items_payload = []
    for item in cart_items:
        sub_total += item.price * item.qty
        items_payload.append({
            'name': item.name,
            'price': item.price,
            'qty': item.qty,
            'total_price': item.price * item.qty
        })

    shipping = 0 if sub_total >= 3000 else 50
    total = sub_total + shipping

    order = Order.objects.create(
        uid=uid,
        sub_total=sub_total,
        shipping=shipping,
        total_amount=total,
        payment_id=request.GET.get('payment_id', ''),
        payment_order_id=request.GET.get('order_id', ''),
        status='paid',
        items_json=items_payload
    )

    cart_items.delete()
    request.session['last_order_id'] = order.id
    
    # Clear delivery address from session after order is placed
    if 'delivery_address' in request.session:
        del request.session['delivery_address']

    return render(request, "success.html", {'order': order})


@login_required
def invoice_pdf(request, order_id):
    uid = User.objects.get(email=request.session['email'])
    order = Order.objects.filter(id=order_id, uid=uid).first()

    if not order:
        messages.error(request, 'Invoice not found.')
        return redirect('cart')

    items = order.items_json or []
    address = Address.objects.filter(uid=uid).order_by('-id').first()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40

    # Company/Website Name Header
    pdf.setFont('Helvetica-Bold', 24)
    pdf.drawString(40, y, 'Digital Electronics')
    
    pdf.setFont('Helvetica', 9)
    y -= 18
    pdf.drawString(40, y, 'Your Premium Electronics Store')
    pdf.drawString(40, y - 12, 'Email: support@digitalelectronics.com | Phone: +91 9876543210')

    # Invoice Title and Details
    y -= 40
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'INVOICE')
    
    pdf.setFont('Helvetica', 10)
    y -= 25
    pdf.drawString(40, y, f"Invoice #: {order.id}")
    pdf.drawString(
        240, y, f"Date: {timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M')}")

    y -= 20
    pdf.drawString(40, y, f"Payment ID: {order.payment_id or 'N/A'}")
    pdf.drawString(240, y, f"Order ID: {order.payment_order_id or 'N/A'}")

    y -= 30
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(40, y, 'Bill To')

    pdf.setFont('Helvetica', 10)
    y -= 15
    pdf.drawString(40, y, f"Name: {uid.name}")
    y -= 15
    pdf.drawString(40, y, f"Email: {uid.email}")
    y -= 15
    pdf.drawString(40, y, f"Phone: {uid.phone_no}")
    y -= 15
    if address:
        pdf.drawString(
            40, y, f"Address: {address.address}, {address.state}, {address.country} - {address.zip_code}")

    y -= 30
    data = [['Product', 'Qty', 'Unit Price', 'Total']]
    for item in items:
        data.append([item.get('name', ''), str(item.get('qty', 0)),
                    f"INR {item.get('price', 0)}", f"INR {item.get('total_price', 0)}"])

    table = Table(data, colWidths=[230, 60, 90, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))

    table_width, table_height = table.wrap(0, 0)
    table.drawOn(pdf, 40, y - table_height)
    y = y - table_height - 30

    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawString(320, y, 'Subtotal:')
    pdf.drawString(420, y, f"INR {order.sub_total}")
    y -= 15
    pdf.drawString(320, y, 'Shipping:')
    pdf.drawString(420, y, f"INR {order.shipping}")
    y -= 15
    pdf.drawString(320, y, 'Total:')
    pdf.drawString(420, y, f"INR {order.total_amount}")

    # Footer
    y -= 40
    pdf.setFont('Helvetica', 9)
    pdf.drawString(40, y, 'Thank you for your purchase! For any queries, please contact us at support@digitalelectronics.com')
    pdf.drawString(40, y - 12, 'Visit us: www.digitalelectronics.com')

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice-{order.id}.pdf"'
    return response


@login_required
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phno = request.POST.get('phno')
        sub = request.POST.get('sub')
        msg = request.POST.get('msg')

        Contact.objects.create(
            name=name,
            email=email,
            phno=phno,
            sub=sub,
            msg=msg
        )
        return redirect('index')

    else:
        return render(request, 'contact.html')


@login_required
def dashboard(request):
    uid = User.objects.get(email=request.session['email'])
    orders = Order.objects.filter(uid=uid).order_by('-created_at')
    address = Address.objects.filter(uid=uid).order_by('-id').first()
    
    context = {
        'uid': uid,
        'orders': orders,
        'address': address
    }
    return render(request, 'dashboard.html', context)


@login_required
def wishlist(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        wid = Wishlist.objects.all()

        con = {
            'uid': uid,
            'wid': wid
        }

        return render(request, 'wishlist.html', con)
    else:
        return render(request, 'wishlist.html')


@login_required
def add_to_wishlist(request, id):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        pid = Add_product.objects.get(id=id)

        Wishlist.objects.create(
            uid=uid,
            pid=pid,
            name=pid.name,
            desc=pid.desc,
            img=pid.img,
            price=pid.price
        )

        return redirect('wishlist')
    else:
        return render(request, 'product_details.html')


@login_required
def remove_wishlist(request, id):
    wid = Wishlist.objects.get(id=id).delete()
    return redirect('wishlist')


@login_required
def about(request):
    return render(request, 'about.html')


@login_required
def blog(request):
    return render(request, 'blog.html')


@login_required
def demo(request):
    return render(request, 'demo.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def ai_page(request):
    uid = User.objects.get(email=request.session['email'])
    return render(request, "ai.html", {"uid": uid})


@login_required
@csrf_exempt
def ai_chat(request):

    if request.method == "POST":

        data = json.loads(request.body)
        message = data.get("message", "").lower()

        reply = "Sorry, I didn't understand. Please ask about products, cart, or categories."

        # Greetings
        if "hello" in message or "hi" in message:
            reply = "Hello! Welcome to our store. How can I help you?"

        elif "how are you" in message:
            reply = "I'm your AI shopping assistant. I'm here to help you find products."

        # TV Questions
        elif "tv" in message or "samsung tv" in message:
            reply = "We have Samsung Neo QLED 4K TV available for ₹50,000. It has excellent display quality."

        # Mobile Questions
        elif "mobile" in message or "oneplus" in message:
            reply = "OnePlus 12 5G is available for ₹25,000. It has great performance and camera."

        # Laptop Questions
        elif "laptop" in message or "macbook" in message:
            reply = "Apple MacBook Air M3 is available for ₹90,000. It is powerful and lightweight."

        # Camera Questions
        elif "camera" in message or "canon" in message:
            reply = "Canon EOS R6 Mark II is available for ₹40,000. It is perfect for professional photography."

        # Watch Questions
        elif "watch" in message or "apple watch" in message:
            reply = "Apple Watch Series 9 is available for ₹15,000. It supports health tracking."

        # AirPods Questions
        elif "airpods" in message or "buds" in message:
            reply = "Apple AirPods Pro 2nd Gen is available with excellent sound quality."

        # Cart Questions
        elif "cart" in message:
            reply = "You can add products to cart and checkout easily."

        # Price Questions
        elif "price" in message:
            reply = "All product prices are shown on the category page."

        # Recommendation Questions
        elif "best product" in message:
            reply = "MacBook Air M3 and OnePlus 12 5G are currently best-selling products."

        elif "cheap product" in message:
            reply = "Apple Watch Series 9 is one of the most affordable products."

        elif "expensive product" in message:
            reply = "MacBook Air M3 is the most premium product available."

        # Help Questions
        elif "help" in message:
            reply = "You can ask about TV, Mobile, Laptop, Camera, Watch, AirPods, or Cart."

        return JsonResponse({"reply": reply})


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not email or not new_password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'forgot_password.html')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Email not found in our system.')
            return render(request, 'forgot_password.html')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'forgot_password.html')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'forgot_password.html')

        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Password must include an uppercase letter.')
            return render(request, 'forgot_password.html')

        if not re.search(r'[a-z]', new_password):
            messages.error(request, 'Password must include a lowercase letter.')
            return render(request, 'forgot_password.html')

        if not re.search(r'\d', new_password):
            messages.error(request, 'Password must include a number.')
            return render(request, 'forgot_password.html')

        if not re.search(r'[^A-Za-z0-9]', new_password):
            messages.error(request, 'Password must include a symbol.')
            return render(request, 'forgot_password.html')

        user.password = new_password
        user.save()
        messages.success(request, 'Password reset successfully! Please login with your new password.')
        return redirect('login')
    else:
        return render(request, 'forgot_password.html')