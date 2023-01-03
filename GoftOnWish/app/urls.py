from app import views
from django.urls import path

urlpatterns = [
    path('',views.Index,name='index'),
    path('login/',views.Login_view,name='login'),
    path('signup/',views.Signup_view,name='signup'),
    path('logout/',views.Logout_view,name='logout'),
    path('profile/', views.Profile, name='profile'),
    path('products/', views.Products, name='products'),
    path('products/<str:id>', views.Product_detail, name='product'),
    path('category/', views.Category, name='category'),
    path('category/<str:name>', views.Categories_view, name='categories'),
    path('contact/', views.Contact, name='contact'),
    path('about/', views.About, name='about'),
    path('cart/', views.Cart_view, name='cart'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path('update_item/',views.updateItem,name="update_item"),
    path('checkout/', views.checkout, name='checkout'),
    path('shippindaddress/', views.shippingAddress, name='shippindaddress'),
    path('payment/',views.payment,name='payment'),
]
