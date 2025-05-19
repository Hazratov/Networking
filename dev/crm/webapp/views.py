from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, CreateRecordForm, UpdateRecordForm, CreateLeadForm, \
    CreateCommunicationForm, UpdateCommunicationForm, UpdateLeadForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate

from django.contrib.auth.decorators import login_required

from .models import Record, Lead, Communication

from django.contrib import messages



# - Homepage 

def home(request):

    return render(request, 'webapp/index.html')


# - Register a user

def register(request):

    form = CreateUserForm()

    if request.method == "POST":

        form = CreateUserForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Account created successfully!")

            return redirect("my-login")

    context = {'form':form}

    return render(request, 'webapp/register.html', context=context)


# - Login a user

def my_login(request):

    form = LoginForm()

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect("dashboard")

    context = {'form':form}

    return render(request, 'webapp/my-login.html', context=context)


# - Dashboard

@login_required(login_url='my-login')
def dashboard(request):
    my_records = Record.objects.filter(created_by=request.user)
    my_leads = Lead.objects.filter(assigned_to=request.user)
    my_communications = Communication.objects.filter(customer__created_by=request.user)

    # CHART DATA
    lead_status_data = my_leads.values('status').annotate(count=Count('id'))
    comm_type_data = my_communications.values('type').annotate(count=Count('id'))

    lead_status_labels = [item['status'] for item in lead_status_data]
    lead_status_counts = [item['count'] for item in lead_status_data]

    comm_type_labels = [item['type'] for item in comm_type_data]
    comm_type_counts = [item['count'] for item in comm_type_data]

    # LATEST 5 RECORDS
    latest_customers = my_records.order_by('-id')[:5]
    latest_leads = my_leads.order_by('-id')[:5]
    latest_comms = my_communications.order_by('-id')[:5]

    # PAGINATE (optional if using pagination elsewhere)
    record_paginator = Paginator(my_records, 10)
    records_page = record_paginator.get_page(request.GET.get('record_page'))

    context = {
        'records': records_page,
        'leads': my_leads,
        'communications': my_communications,
        'lead_status_labels': lead_status_labels,
        'lead_status_counts': lead_status_counts,
        'comm_type_labels': comm_type_labels,
        'comm_type_counts': comm_type_counts,
        'latest_customers': latest_customers,
        'latest_leads': latest_leads,
        'latest_comms': latest_comms,
    }

    return render(request, 'webapp/dashboard.html', context)


# list customer

def customer_table_view(request):
    records = Record.objects.all()
    record_page = request.GET.get('record_page')
    record_paginator = Paginator(records, 10)
    record_obj = record_paginator.get_page(record_page)
    return render(request, 'webapp/customers_table.html', {'records': record_obj})

def lead_table_view(request):
    leads = Lead.objects.all()
    lead_page = request.GET.get('lead_page')
    lead_paginator = Paginator(leads, 10)
    lead_obj = lead_paginator.get_page(lead_page)
    return render(request, 'webapp/leads_table.html', {'leads': lead_obj})

def communication_table_view(request):
    communications = Communication.objects.all()
    comm_page = request.GET.get('comm_page')
    comm_paginator = Paginator(communications, 10)
    comm_obj = comm_paginator.get_page(comm_page)
    return render(request, 'webapp/communications_table.html', {'communications': comm_obj})

# - Create a record 

@login_required(login_url='my-login')
def create_record(request):
    form = CreateRecordForm()
    if request.method == "POST":
        form = CreateRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            messages.success(request, "Your client was created!")
            return redirect("dashboard")
    context = {'form': form}
    return render(request, 'webapp/create-record.html', context)


# - Update a record 

@login_required(login_url='my-login')
def update_record(request, pk):

    record = Record.objects.get(id=pk)

    form = UpdateRecordForm(instance=record)

    if request.method == 'POST':

        form = UpdateRecordForm(request.POST, instance=record)

        if form.is_valid():

            form.save()

            messages.success(request, "Your record was updated!")

            return redirect("dashboard")
        
    context = {'form':form}

    return render(request, 'webapp/update-record.html', context=context)


# LEAD UPDATE
@login_required(login_url='my-login')
def update_lead(request, pk):
    lead = Lead.objects.get(id=pk)
    form = UpdateLeadForm(instance=lead)
    if request.method == "POST":
        form = UpdateLeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead updated successfully!")
            return redirect("leads-table")
    return render(request, 'webapp/update-lead.html', {'form': form})


# COMMUNICATION UPDATE
@login_required(login_url='my-login')
def update_communication(request, pk):
    com = Communication.objects.get(id=pk)
    form = UpdateCommunicationForm(instance=com)
    if request.method == "POST":
        form = UpdateCommunicationForm(request.POST, instance=com)
        if form.is_valid():
            form.save()
            messages.success(request, "Communication updated successfully!")
            return redirect("communications-table")
    return render(request, 'webapp/update-communication.html', {'form': form})

# - Read / View a singular record

@login_required(login_url='my-login')
def singular_record(request, pk):

    all_records = Record.objects.get(id=pk)

    context = {'record':all_records}

    return render(request, 'webapp/view-record.html', context=context)


# - Delete a record

@login_required(login_url='my-login')
def delete_record(request, pk):

    record = Record.objects.get(id=pk)

    record.delete()

    messages.success(request, "Your record was deleted!")

    return redirect("dashboard")



# - User logout

def user_logout(request):

    auth.logout(request)

    messages.success(request, "Logout success!")

    return redirect("my-login")


# - List all leads
@login_required(login_url='my-login')
def lead_list(request):
    leads = Lead.objects.all()
    context = {'leads': leads}
    return render(request, 'webapp/lead-list.html', context)

# - Create a lead
@login_required(login_url='my-login')
def create_lead(request):
    form = CreateLeadForm()
    if request.method == "POST":
        form = CreateLeadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead created!")
            return redirect("dashboard")
    return render(request, 'webapp/create-lead.html', {'form': form})

# - List communication logs
@login_required(login_url='my-login')
def communication_list(request):
    logs = Communication.objects.all()
    context = {'logs': logs}
    return render(request, 'webapp/communication-list.html', context)

# - Create a communication log
@login_required(login_url='my-login')
def create_communication(request):
    form = CreateCommunicationForm()
    if request.method == "POST":
        form = CreateCommunicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Communication log saved!")
            return redirect("dashboard")
    return render(request, 'webapp/create-communication.html', {'form': form})




