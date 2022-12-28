from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class MyCustomerManager(BaseUserManager):
    def create_user(self, email ,first_name,last_name, mobile, password=None):
        if not email:
            raise ValueError("User must have email address.")
        if not first_name:
            raise ValueError("Users must have an first name")
        if not last_name:
            raise ValueError("Users must have an last name")
        if not mobile:
            raise ValueError("Users must have an mobile")
        

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            mobile = mobile,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, mobile, password):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            mobile=mobile,
            password= password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Customer(AbstractBaseUser):
    first_name = models.CharField(verbose_name='first name',max_length=30)
    last_name = models.CharField(verbose_name='last name',max_length=30)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    mobile = models.CharField(verbose_name='mobile no', max_length=12)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile']

    objects = MyCustomerManager()

    def __str__(self):
        return self.email
    
    
    # Checking for permission
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
CATEGORY = (
    ('Birthday', 'Birthday'),
    ('Cakes', 'Cakes'),
    ('Flowers', 'Flowers'),
    ('Toys', 'Toys'),
    
)

class Product(models.Model):
    name = models.CharField(max_length=30)
    o_price = models.FloatField(verbose_name='Original Price')
    d_price = models.FloatField(verbose_name='Discounted Price')
    category = models.CharField(choices=CATEGORY, max_length=20)
    star = models.IntegerField()
    unit = models.CharField(max_length=5)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def get_discount(self):
        discont = ((self.o_price - self.d_price) / self.o_price) * 100
        return discont
    

    @property
    def imageUrl(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url