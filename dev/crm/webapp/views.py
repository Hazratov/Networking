from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, CreateRecordForm, UpdateRecordForm, CreateLeadForm, CreateCommunicationForm

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

    context = {
        'records': my_records,
        'leads': my_leads,
        'communications': my_communications,
    }

    return render(request, 'webapp/dashboard.html', context=context)


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




