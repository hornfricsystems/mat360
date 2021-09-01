from django.urls import path

from home import views
from traveller import  views as tview
app_name='home'
urlpatterns=[
    path('',views.Index.as_view(),name='index'),
    path('saccos/',views.Saccos.as_view(),name='saccos'),
    path('book_ride/',views.book_ride,name='book-ride'),
    path('signin/',tview.log_user_in,name='signin'),
    path('signup/',tview.create_customer_account,name='signup'),
    path('logout/',views.logout_view,name='logout'),


   #validation ajax requests
    path('ajax/list_sacco/',views.check_saccos,name='check-saccos'),
    path('ajax/list_rides/', views.get_sacco_rides, name='listrides'),
    #path('ajax/get_ride_details/', views.get_ride_details, name='getridedetails'),
    path('ajax/get-active-fare/', views.getActivePrice, name='getactivefare'),
    path('ajax/ride_details/',views.get_ride_important_details,name='rideimportantdetails'),
    path('confirmation/',views.confirmation_url,name='confirmation'),
    path('validation/',views.validation_url,name='validation'),
    path('try-payments/',views.process_payment,name='mobile_payment'),

]