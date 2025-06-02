from django.urls import path

from . import views

urlpatterns = [

    path('', views.home, name="home"),
    path('register', views.register, name="register"),
    path('my-login', views.my_login, name="my-login"),
    path('user-logout', views.user_logout, name="user-logout"),
    # CRUD
    path('dashboard', views.dashboard, name="dashboard"),
    path('create-record', views.create_record, name="create-record"),
    path('update-record/<int:pk>', views.update_record, name='update-record'),
    path('record/<int:pk>', views.singular_record, name="record"),
    path('delete-record/<int:pk>', views.delete_record, name="delete-record"),

    # Leads
    path('leads', views.lead_list, name='lead-list'),
    path('leads/create', views.create_lead, name='create-lead'),

    # Communication logs
    path('communications', views.communication_list, name='communication-list'),
    path('communications/create', views.create_communication, name='create-communication'),

    #list customer
    path('customers-table/', views.customer_table_view, name='customers-table'),
    path('leads-table/', views.lead_table_view, name='leads-table'),
    path('communications-table/', views.communication_table_view, name='communications-table'),
    path('update-lead/<int:pk>/', views.update_lead, name='update-lead'),
    path('update-communication/<int:pk>/', views.update_communication, name='update-communication'),

]






