from django.urls import path

from traveller import views
from  home import views as home_view
app_name='traveller'

urlpatterns=[
  path('accounts/travellerdash/',views.load_traveller_dashboard,name='t-dash'),
  path('accounts/bookride/',views.home_book_ride,name='bookride'),
  path('accounts/myrides/',views.my_rides,name='myrides'),
  path('accounts/pay_ride',views.pay_your_ride,name='pay_ride'),

]