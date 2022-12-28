from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from app.forms import SignupForm, AccountAuthenticationForm
from app.models import Customer,Product
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

    return render(request,'app/contact.html', {})
def About(request):

    return render(request, 'app/about.html', {})

def Cart_view(request):

    return render(request, 'app/cart.html', {})


    