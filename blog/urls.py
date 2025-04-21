from django.urls import path
from . import views
from dmproject.settings import collection

urlpatterns = [
    path('', views.index,name='index'),
    path('add', views.add,name='add'),
    path('users', views.users,name='users'),
    path('update/<id>', views.update,name='update'),
    path('delete/<id>', views.delete,name='delete'),
    path('login/', views.login,name='login'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('logout/', views.logout,name='logout'),
    path('add_product', views.add_product,name='add_product'),
    path('order/<id>', views.order,name='order'),
    path("order_list", views.order_list, name="order_list"),
    path('payment_success', views.payment_success, name='payment_success'),
]
