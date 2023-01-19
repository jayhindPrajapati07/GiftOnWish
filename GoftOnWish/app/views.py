import datetime
import json
from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse,JsonResponse
from app.forms import SignupForm, AccountAuthenticationForm,QueriesForm,NewsletterForm,ReviewForm
from app.models import Customer,Product,OrderItem,Order,ShippingAddress,ProductReview
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
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
from django.contrib.sites.shortcuts import get_current_site
from app.utils import generate_token
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
                messages.success(request, 'Logged in Sucessfully!!')
                return redirect("index")
    else:
        form = AccountAuthenticationForm()

    return render(request, 'registration/login.html', {'login_form':form})
   
def Logout_view(request):
    logout(request)
    messages.success(request,"Logged out Sucessfully!!")
    return redirect("index") 

def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('registration/activate.txt', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    admin_email = settings.EMAIL_HOST_USER
    try:
        send_mail(email_subject, email_body, admin_email , [user.email], fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')

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
            u = Customer.objects.get(email=email)
            send_activation_email(u, request)
            url = request.META.get('HTTP_REFERER')
            messages.success(request, 'Please verify your email by clicking on link we have sent on your email!!')
            return redirect(url)
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
    review = ProductReview.objects.filter(product__id=id, status=True)

    purchased =[]
    if request.user.is_authenticated:

        purchased = purchasedItem(request.user, id)

    
    order= cart(request)
    return render(request, 'app/product_detail.html', {'product':product,'order':order,'reviews':review, 'purchased':purchased})

def purchasedItem(customer, id):
        order = Order.objects.filter(customer=customer, complete=True, delivered=True)
        items=[]
        for i in range(len(order)):
            a = order[i].orderitem_set.filter(product__id=id).values()
            for j in range(len(a)):
                items.append(a[j]['product_id'])
        return items

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
    url = request.META.get('HTTP_REFERER')
    context ={}
    if request.POST:
        if request.user.is_authenticated:

            form = QueriesForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'we have recieved your query. We will try our best to solve your query. Thank you!!')
                return redirect(url)
            else:
                context['contact_form'] =form
        else:
            messages.error(request, 'Please login to send query!!')
            form = QueriesForm()
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
                messages.success(request, 'Address added sucessfully!!')
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
    url = request.META.get('HTTP_REFERER')
    if request.POST:
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have sucessfully subscribed for Newsletter.')
            return redirect(url)
        else:
            messages.error(request, 'Something went wrong!')
            return redirect(url)




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
                        messages.error(request, 'Something went wrong!!')
                    
                    url = request.META.get('HTTP_REFERER')
                    messages.success(request,"We've emailed your instructions for setting your password, if an account exists with the email you entered. You should receive them shortly.If you don't receive an email, please make sure you've entered the email address you registered with, and check your spam folder.")
                    return redirect (url)
            
            messages.error(request, 'Email is not registered!')
            return redirect('password_reset')

    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})

def activate_user(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = Customer.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Your email is now Verified!! Now you can login into your account.')
        return redirect('login')

    return render(request, 'registration/activate_failed.html', {"user": user})
    
    
def submit_review(request, p_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ProductReview.objects.get(customer__id=request.user.id, product__id=p_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ProductReview.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ProductReview()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.product_id = p_id
                data.customer_id = request.user.id
                data.save()
                # messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)