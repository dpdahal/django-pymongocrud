from django.urls import path
from . import views
from dmproject.settings import collection

urlpatterns = [
    path('', views.index,name='index'),
    path('add', views.add,name='add'),
    path('update/<id>', views.update,name='update'),
    path('delete/<id>', views.delete,name='delete'),
     path('login/', views.login,name='login'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('logout/', views.logout,name='logout'),
]
