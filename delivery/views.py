from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from .models import Customer, Restaurant, Item, Cart

import razorpay
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'delivery/index.html')

def open_signin(request):
    return render(request, 'delivery/signin.html')

def open_signup(request):
    return render(request, 'delivery/signup.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        try:
            Customer.objects.get(username = username)
            return HttpResponse("Duplicate username!")
        except:
            Customer.objects.create(
                username = username,
                password = password,
                email = email,
                mobile = mobile,
                address = address,
            )
    return render(request, 'delivery/signin.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            Customer.objects.get(username=username, password=password)

            if username == 'admin':
                return render(request, 'delivery/admin_dashboard.html')
            else:
                return redirect('customer_home', username=username)

        except Customer.DoesNotExist:
            return render(request, 'delivery/fail.html')

    return render(request, 'delivery/signin.html')
    
def admin_dashboard(request):
    restaurant_count = Restaurant.objects.count()
    item_count = Item.objects.count()
    customer_count = Customer.objects.count()
    cart_count = Cart.objects.count()

    return render(request, 'delivery/admin_dashboard.html', {
        'restaurant_count': restaurant_count,
        'item_count': item_count,
        'customer_count': customer_count,
        'cart_count': cart_count,
    })

def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        try:
            Restaurant.objects.get(name = name)
            return HttpResponse("Duplicate restaurant!")
        except:
            Restaurant.objects.create(
                name = name,
                picture = picture,
                cuisine = cuisine,
                rating = rating,
            )
    return render(request, 'delivery/admin_home.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})

def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'delivery/update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})


def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})


def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'delivery/update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})
    
def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')
        
        try:
            Item.objects.get(name = name, restaurant = restaurant)
            return HttpResponse("Duplicate item!")
        except:
            Item.objects.create(
                restaurant = restaurant,
                name = name,
                description = description,
                price = price,
                vegeterian = vegeterian,
                picture = picture,
            )
    return open_update_menu(request, restaurant_id)

def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    itemList = restaurant.items.all()

    food_type = request.GET.get('type')

    if food_type == 'veg':
        itemList = itemList.filter(vegeterian=True)

    elif food_type == 'nonveg':
        itemList = itemList.filter(vegeterian=False)

    return render(
        request,
        'delivery/customer_menu.html',
        {
            'itemList': itemList,
            'restaurant': restaurant,
            'username': username,
            'food_type': food_type
        }
    )

def add_to_cart(request, item_id, username):
    item = Item.objects.get(id=item_id)
    customer = Customer.objects.get(username=username)

    cart, created = Cart.objects.get_or_create(customer=customer)

    # Prevent items from different restaurants
    if cart.items.exists():
        first_item = cart.items.first()

        if first_item.restaurant_id != item.restaurant_id:
            restaurant = item.restaurant

            return render(request, 'delivery/customer_menu.html', {
                'itemList': restaurant.items.all(),
                'restaurant': restaurant,
                'username': username,
                'cart_error': 'Your cart already contains items from another restaurant.'
            })

    # Add item to cart
    cart.items.add(item)

    # Get current quantity
    quantities = cart.quantities or {}
    item_id_str = str(item.id)

    if item_id_str in quantities:
        quantities[item_id_str] += 1
    else:
        quantities[item_id_str] = 1

    cart.quantities = quantities
    cart.save()

    restaurant = item.restaurant

    return render(request, 'delivery/customer_menu.html', {
        'itemList': restaurant.items.all(),
        'restaurant': restaurant,
        'username': username,
        'cart_success': f'{item.name} added to cart!'
    })

def show_cart(request, username):
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer=customer).first()

    items = list(cart.items.all()) if cart else []

    # Calculate subtotal
    subtotal = cart.total_price() if cart else 0

    # Delivery fee
    delivery_fee = 40 if items else 0

    # Final total
    total_price = subtotal + delivery_fee

    restaurant = items[0].restaurant if items else None

    if cart:
        quantities = cart.quantities or {}

        for item in items:
            item.cart_quantity = quantities.get(str(item.id), 1)
            item.cart_total = item.price * item.cart_quantity
    else:
        quantities = {}

    return render(request, 'delivery/cart.html', {
        'itemList': items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_price': total_price,
        'username': username,
        'restaurant': restaurant,
        'quantities': quantities
    })

def increase_quantity(request, item_id, username):
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer=customer).first()

    if cart:
        if cart.items.filter(id=item_id).exists():
            quantities = cart.quantities or {}
            item_id_str = str(item_id)

            quantities[item_id_str] = quantities.get(item_id_str, 1) + 1

            cart.quantities = quantities
            cart.save()

    return show_cart(request, username)


def decrease_quantity(request, item_id, username):
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer=customer).first()

    if cart:
        if cart.items.filter(id=item_id).exists():
            quantities = cart.quantities or {}
            item_id_str = str(item_id)

            current_quantity = quantities.get(item_id_str, 1)

            if current_quantity > 1:
                quantities[item_id_str] = current_quantity - 1
            else:
                del quantities[item_id_str]
                cart.items.remove(Item.objects.get(id=item_id))

            cart.quantities = quantities
            cart.save()

    return show_cart(request, username)

def remove_from_cart(request, item_id, username):
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer=customer).first()

    if cart:
        item = Item.objects.get(id=item_id)

        cart.items.remove(item)

        quantities = cart.quantities or {}
        quantities.pop(str(item_id), None)

        cart.quantities = quantities
        cart.save()

    return show_cart(request, username)


def clear_cart(request, username):
    customer = Customer.objects.get(username=username)
    cart = Cart.objects.filter(customer=customer).first()

    if cart:
        cart.items.clear()
        cart.quantities = {}
        cart.save()

    return show_cart(request, username)

def customer_home(request, username):
    search = request.GET.get('search', '').strip()

    if search:
        restaurantList = Restaurant.objects.filter(
            name__icontains=search
        ) | Restaurant.objects.filter(
            cuisine__icontains=search
        )
    else:
        restaurantList = Restaurant.objects.all()

    return render(request, 'delivery/customer_home.html', {
        'restaurantList': restaurantList,
        'username': username,
        'search': search
    })

def profile(request, username):
    customer = Customer.objects.get(username=username)

    return render(request, 'delivery/profile.html', {
        'customer': customer,
        'username': username
    })

def logout(request):
    return render(request, 'delivery/index.html')

# Checkout View
def checkout(request, username):
    # Fetch customer and their cart
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    cart_items = list(cart.items.all()) if cart else []

    restaurant = cart_items[0].restaurant if cart_items else None

    # Calculate subtotal
    subtotal = cart.total_price() if cart else 0

    # Add delivery fee
    delivery_fee = 40 if cart_items else 0

    # Final amount
    total_price = subtotal + delivery_fee

    # Empty cart
    if total_price == 0:
        return render(request, 'delivery/checkout.html', {
            'error': 'Your cart is empty!',
            'username': username,
            'subtotal': 0,
            'delivery_fee': 0,
            'total_price': 0,
            'restaurant': restaurant
        })

    # Initialize Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # Create Razorpay order
    order_data = {
        'amount': int(total_price * 100),
        'currency': 'INR',
        'payment_capture': 1
    }

    order = client.order.create(data=order_data)

    # Pass order details to frontend
    return render(request, 'delivery/checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': int(total_price * 100),
        'restaurant': restaurant
    })

# Orders Page
# Orders Page
def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    # Fetch cart items before clearing the cart
    cart_items = list(cart.items.all()) if cart else []

    # Get quantities before clearing the cart
    quantities = cart.quantities or {} if cart else {}

    # Calculate subtotal
    subtotal = cart.total_price() if cart else 0

    # Delivery fee
    delivery_fee = 40 if cart_items else 0

    # Final total
    total_price = subtotal + delivery_fee

    # Add quantity and item total to each item
    for item in cart_items:
        item.cart_quantity = quantities.get(str(item.id), 1)
        item.cart_total = item.price * item.cart_quantity

    # Clear the cart after fetching all order details
    if cart:
        cart.items.clear()
        cart.quantities = {}
        cart.save()

    return render(request, 'delivery/orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_price': total_price,
    })