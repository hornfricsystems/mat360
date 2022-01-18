from django.urls import path

from mat360admin import views
app_name='mat360admin'

urlpatterns=[
    path('',views.log_admin_in,name='admin-login'),
    path('accounts/',views.load_admin_dash,name='admin-dash'),
    path('create-admin/',views.create_system_admin,name='create-admin'),
    path('all_transactions',views.getFareTransactions,name='all_transactions'),
    path('c2b/register',views.register_urls,name='register_mpesa_validation'),
    path('c2b/confirmation',views.confirmation,name='confirmation'),
    path('c2b/validation',views.validation,name='validation'),
    path('c2b/simulate',views.simulatec2b,name='simulate'),
    path('c2b/lipanampesa',views.lipaNaMpesaOnline,name='lipanampesa'),
    path('admin/accounts/sacco_requests_applications/',views.view_sacco_requests_applications_and_approve,name='admin-sacco-application-requests'),
    path('admin/accounts/approved_applications/',views.ApprovedSaccoRequests.as_view(),name='approved_sacco_requests'),

]