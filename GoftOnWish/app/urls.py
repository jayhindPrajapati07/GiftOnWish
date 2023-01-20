from app import views
from django.urls import path

urlpatterns = [
    path('',views.Index,name='index'),
    path('login/',views.Login_view,name='login'),
    path('signup/',views.Signup_view,name='signup'),
    path('logout/',views.Logout_view,name='logout'),
    path('activate-user/<uidb64>/<token>',views.activate_user, name='activate'),
    
    path('profile/', views.Profile, name='profile'),
    path('products/', views.Products, name='products'),
    path('products/<str:id>', views.Product_detail, name='product'),
    path('category/', views.Category, name='category'),
    path('category/<str:name>', views.Categories_view, name='categories'),
    path('contact/', views.Contact, name='contact'),
    path('about/', views.About, name='about'),
    path('review/<int:p_id>/', views.submit_review, name='review'),
    
    path('cart/', views.Cart_view, name='cart'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path('update_item/',views.updateItem,name="update_item"),
    
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/change_address', views.change_addrs, name='change_address'),
    path('shippindaddress/', views.shippingAddress, name='shippindaddress'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
    
]
