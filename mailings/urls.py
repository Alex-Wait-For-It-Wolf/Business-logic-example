from django.urls import path, include

from . import views

urlpattenrs = [
    path('add_to_common_list', views.add_to_common_list_view),
    path('add_to_case_list', views.add_to_case_list_view),
    
    # Part 3
    path('add_to_common_list', views.add_email_to_common_mailchimp_list_view),
    path('add_to_case_list', views.add_email_to_case_mailchimp_list_view),

]
