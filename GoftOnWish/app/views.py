from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from app.forms import SignupForm, AccountAuthenticationForm,QueriesForm,NewsletterForm
from app.models import Customer,Product

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

# Create your views here.
def Index(request):
    products = Product.objects.order_by("?")[:12]
    return render(request,"app/index.html",{'products':products})

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
    user_id = request.user.id
    customer = Customer.objects.get(pk=user_id)
    return render(request, 'app/profile.html', {'customer':customer})

def Products(request):
    products = Product.objects.all()
    starcount = Product.star
    return render(request, 'app/product.html', {'products':products,'starcount':starcount})

def Product_detail(request,id):
    product_id = id
    product = Product.objects.get(pk=product_id)
    return render(request, 'app/product_detail.html', {'product':product})

def Category(request):
    birthday = Product.objects.filter(category='Birthday').all()
    cakes = Product.objects.filter(category='Cakes').all()
    flowers = Product.objects.filter(category='Flowers').all()
    toys = Product.objects.filter(category='Toys').all()
    


    context = {'birthday':birthday, 'cakes':cakes, 'flowers': flowers, 'toys':toys,}

    return render(request, 'app/category.html', context)

def Categories_view(request, name):
    category  = name
    p = Product.objects.filter(category=category).all()

    return render(request, 'app/categories_specific.html', {'products':p, 'category':category})

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
    return render(request,'app/contact.html', {'contact_form':form})

def About(request):

    return render(request, 'app/about.html', {})

def Cart_view(request):

    return render(request, 'app/cart.html', {})


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


    