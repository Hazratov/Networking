from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, CreateRecordForm, UpdateRecordForm, CreateLeadForm, \
    CreateCommunicationForm, UpdateCommunicationForm, UpdateLeadForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.utils.timezone import now, timedelta
from django.contrib.auth.decorators import login_required

from .models import Record, Lead, Communication, ActivityLog
from django.db.models.functions import TruncMonth
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
    user = request.user

    my_records = Record.objects.filter(created_by=user)
    my_leads = Lead.objects.filter(assigned_to=user)
    my_communications = Communication.objects.filter(customer__created_by=user)

    # Charts: Leads + Comms
    lead_status_data = my_leads.values('status').annotate(count=Count('id'))
    comm_type_data = my_communications.values('type').annotate(count=Count('id'))

    lead_status_labels = [item['status'] for item in lead_status_data]
    lead_status_counts = [item['count'] for item in lead_status_data]

    comm_type_labels = [item['type'] for item in comm_type_data]
    comm_type_counts = [item['count'] for item in comm_type_data]

    # Chart: Customer Growth
    customer_growth = (
        my_records.annotate(month=TruncMonth('creation_date'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    customer_growth_labels = [entry['month'].strftime('%b %Y') for entry in customer_growth]
    customer_growth_counts = [entry['total'] for entry in customer_growth]

    # Chart: Customers by Country
    customers_by_country = (
        my_records.values('country')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    country_labels = [c['country'] for c in customers_by_country]
    country_counts = [c['total'] for c in customers_by_country]

    # KPIs
    total_customers = my_records.count()
    total_leads = my_leads.count()
    total_communications = my_communications.count()

    qualified = my_leads.filter(status='qualified').count()
    closed = my_leads.filter(status='closed').count()
    lead_conversion_rate = 0
    if total_leads > 0:
        lead_conversion_rate = round((qualified + closed) / total_leads * 100)

    # Latest + Upcoming
    latest_customers = my_records.order_by('-id')[:5]
    latest_leads = my_leads.order_by('-id')[:5]
    latest_comms = my_communications.order_by('-id')[:5]
    upcoming_communications = my_communications.filter(
        date__gte=now(),
        date__lte=now() + timedelta(days=7)
    ).order_by('date')

    # Activity Feed
    recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:10]

    context = {
        'records': my_records,
        'leads': my_leads,
        'communications': my_communications,
        'lead_status_labels': lead_status_labels,
        'lead_status_counts': lead_status_counts,
        'comm_type_labels': comm_type_labels,
        'comm_type_counts': comm_type_counts,
        'customer_growth_labels': customer_growth_labels,
        'customer_growth_counts': customer_growth_counts,
        'country_labels': country_labels,
        'country_counts': country_counts,
        'total_customers': total_customers,
        'total_leads': total_leads,
        'total_communications': total_communications,
        'lead_conversion_rate': lead_conversion_rate,
        'latest_customers': latest_customers,
        'latest_leads': latest_leads,
        'latest_comms': latest_comms,
        'upcoming_communications': upcoming_communications,
        'recent_activities': recent_activities,
    }

    return render(request, 'webapp/dashboard.html', context)
# list customer

def customer_table_view(request):
    query = request.GET.get('q', '')  # Get search query if any
    records = Record.objects.all()

    if query:
        records = records.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(city__icontains=query) |
            Q(country__icontains=query)
        )

    record_page = request.GET.get('record_page')
    record_paginator = Paginator(records, 10)
    record_obj = record_paginator.get_page(record_page)

    return render(request, 'webapp/customers_table.html', {
        'records': record_obj,
        'search_query': query,
    })
def lead_table_view(request):
    query = request.GET.get('q', '')
    leads = Lead.objects.select_related('customer', 'assigned_to').all()

    if query:
        leads = leads.filter(
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(status__icontains=query) |
            Q(assigned_to__username__icontains=query)
        )

    lead_page = request.GET.get('lead_page')
    lead_paginator = Paginator(leads, 10)
    lead_obj = lead_paginator.get_page(lead_page)

    return render(request, 'webapp/leads_table.html', {
        'leads': lead_obj,
        'search_query': query,
    })

def communication_table_view(request):
    query = request.GET.get('q', '')
    communications = Communication.objects.select_related('customer').all()

    if query:
        communications = communications.filter(
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(type__icontains=query)
        )

    comm_page = request.GET.get('comm_page')
    comm_paginator = Paginator(communications, 10)
    comm_obj = comm_paginator.get_page(comm_page)

    return render(request, 'webapp/communications_table.html', {
        'communications': comm_obj,
        'search_query': query,
    })
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

    messages.success(request, "Your customer was deleted!")

    return redirect("customers-table")


# - Delete a lead

@login_required(login_url='my-login')
def delete_lead(request, pk):

    leads = Lead.objects.get(id=pk)

    leads.delete()

    messages.success(request, "Your lead was deleted!")

    return redirect("leads-table")

# - Delete a Communications

@login_required(login_url='my-login')
def delete_communication(request, pk):

    communications = Communication.objects.get(id=pk)

    communications.delete()

    messages.success(request, "Your communication was deleted!")

    return redirect("communications-table")




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




