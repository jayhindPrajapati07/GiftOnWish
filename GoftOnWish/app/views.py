import datetime
import json
from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse,JsonResponse
from app.forms import SignupForm, AccountAuthenticationForm,QueriesForm,NewsletterForm
from app.models import Customer,Product,OrderItem,Order,ShippingAddress

# Password reset import
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.conf import settings

import stripe

def cart(req):
    if req.user.is_authenticated:
        customer = req.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        return order
        
        

# Create your views here.
def Index(request):
    products = Product.objects.all()[:12]
    order= cart(request)
    return render(request,"app/index.html",{'products':products ,'order':order })

def Login_view(request):
    user = request.user
    if user.is_authenticated: 
        return redirect("index")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect("index")
    else:
        form = AccountAuthenticationForm()

    return render(request, 'registration/login.html', {'login_form':form})
   
def Logout_view(request):
	logout(request)
	return redirect("index") 

def Signup_view(request):
    user = request.user

    if user.is_authenticated:
        return redirect('index')
    
    context = {}
    if request.POST:
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            customer = authenticate(email=email, password=raw_password)
            
            login(request, customer)
            return redirect('index')
        else:
            context['signup_form'] = form

    else:
        form = SignupForm()
    
    return render(request, 'registration/signup.html', {'signup_form':form})

def Profile(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        customer = Customer.objects.get(pk=user_id)
        
        
        address = ShippingAddress.objects.filter(customer=customer)
        order_detail = Order.objects.filter(customer=customer, complete=True)
    else:
        return redirect('login')
    order= cart(request)
    return render(request, 'app/profile.html', {'customer':customer,'order':order,'address':address,'order_detail':order_detail})

def Products(request):
    products = Product.objects.all()
    starcount = Product.star
    order= cart(request)
    return render(request, 'app/product.html', {'products':products,'starcount':starcount,'order':order})

def Product_detail(request,id):
    product_id = id
    product = Product.objects.get(pk=product_id)
    order= cart(request)
    return render(request, 'app/product_detail.html', {'product':product,'order':order})

def Category(request):
    birthday = Product.objects.filter(category='Birthday').all()
    cakes = Product.objects.filter(category='Cakes').all()
    flowers = Product.objects.filter(category='Flowers').all()
    toys = Product.objects.filter(category='Toys').all()
    

    order= cart(request)
    context = {'birthday':birthday, 'cakes':cakes, 'flowers': flowers, 'toys':toys,'order':order}
    
    return render(request, 'app/category.html', context,)

def Categories_view(request, name):
    category  = name
    p = Product.objects.filter(category=category).all()
    order= cart(request)
    return render(request, 'app/categories_specific.html', {'products':p, 'category':category,'order':order})

def Contact(request):

    context ={}
    if request.POST:
        if request.user.is_authenticated:

            form = QueriesForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, 'app/sent.html')
            else:
                context['contact_form'] =form
        else:
            return HttpResponse('Please Login to send query!!')
    else:
        form = QueriesForm()
    order= cart(request)
    return render(request,'app/contact.html', {'contact_form':form,'order':order})

def About(request):
    order= cart(request)
    return render(request, 'app/about.html', {'order':order})


def Cart_view(request):
    if request.user.is_authenticated:
        customer = request.user
        order,created = Order.objects.get_or_create(customer =customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
     

        context={'items':items,'order':order,'cartItems':cartItems}
        return render(request, 'app/cart.html', context)

def shippingAddress(request):
    if request.user.is_authenticated:
        customer= request.user
        if request.POST:
            
                addr=request.POST['address']
                landmark=request.POST['landmark']
                zipcode=request.POST['zipcode']
                city=request.POST['city']
                state=request.POST['state']
                
                add1=ShippingAddress.objects.create(customer=customer, address=addr,landmark=landmark,zipcode=zipcode,city=city,state=state)
                
                add1.save()
                
        return redirect('checkout')

def checkout(request):
    context={}
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
        address = ShippingAddress.objects.filter(customer=customer)
        amount = int(order.get_cart_total*100)
        key =settings.STRIPE_PUBLISHABLE_KEY
        
        
    else:
        return redirect('login')

    context ={'items':items, 'order':order, 'cartItem':cartItem,'address':address,'amount':amount,'key':key}

    return render(request, 'app/checkout.html', context)

stripe.api_key=settings.STRIPE_SECRET_KEY

def process_payment(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            customer = request.user
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            amount = int(order.get_cart_total * 100)
            address = ShippingAddress.objects.filter(customer=customer).values()
            
            stripe.PaymentIntent.create(
                amount=amount,
                currency="inr",
                payment_method_types=["card"],
            )

            order.transaction_id = datetime.datetime.now().timestamp()
            order.complete = True
            order.date_completed = datetime.date.today()
            order.save()

    return render(request, 'payment/payment_status.html', {'order':order ,'customer':customer,'address':address, 'items':items})

def invoice(request, id):
    order_id = id
    if request.user.is_authenticated:
        customer = request.user
        order= Order.objects.get(pk=order_id)
        items = order.orderitem_set.all()
        address = ShippingAddress.objects.filter(customer=customer).values()


    return render(request, 'payment/invoice.html', {'order':order, 'address':address, 'customer':customer, 'items':items})


def updateItem(request):
    data = json.loads(request.body)
    productId=data['productId']
    action = data['action']
    print('Action: ',action)
    print('ProductId: ',productId)
    
    customer =request.user
    product = Product.objects.get(id=productId)
    order,created = Order.objects.get_or_create(customer=customer,complete=False)
    
    orderItem,created = OrderItem.objects.get_or_create(order=order,product=product)
    
    if action =='add':
        orderItem.quantity=(orderItem.quantity + 1)
    elif action =='remove':
        orderItem.quantity = (orderItem.quantity -1)
    orderItem.save()
    
    if orderItem.quantity <=0:
        orderItem.delete()
        
    return JsonResponse("Item was added",safe=False)


def newsletter(request):
    if request.POST:
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'app/newsletter.html')




def password_reset_request(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = Customer.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = 'Password Reset Requested'
                    email_template_name = 'password/password_reset_email.txt'
                    c = {
                        "email":user.email,
                        'domain':'127.0.0.1:8000',
                        'site_name': 'GiftOnWish',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    admin_email = settings.EMAIL_HOST_USER
                    try:
                        send_mail(subject, email, admin_email , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("password_reset_done")
            
            messages.error(request, 'Email is not registered!')
            return redirect('password_reset')

    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})


    