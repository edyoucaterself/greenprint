#views.py
# Created On: 9/5/2016
# Created By: Matt Agresta
#-----------------------------------------------------------#
#Set up Environment
import ast

from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse

from .forms import ExpensesForm, IncomeForm, EditForm, CategoriesForm
from .forms import UserCreateForm, UserCatForm, UserProfileForm
from .models import Items, BudgetData, Categories, UserCat
from .budget import Budget


#Function to load Expenses Form with previous Data
#Need to pass category added to this and set it in forminit
def expensesformload(request, **kwargs):
    #Grab Data from form before edit button was pressed
    formdata = request.POST['formdata']
    #Translate string back to dict
    formdata = formdata[11:]
    formdata = formdata[:-1]
    formdata = formdata.replace("[u","")
    formdata = formdata.replace("]","")
    forminit = eval(formdata)
    #Set initial category
    #Not working
    if 'category' in kwargs:
        cat = kwargs['category']
        forminit['category'] = cat
    #Load initial values into forms
    form = ExpensesForm(initial=forminit,
                        userid=request.user)
    return form


#Function to load UserCat Form
#To Be called by a view, returns form
def usercatformload(request):
    #Try and get UserCat object for user
    #Should have been created on user creation
    try:
        initcat = UserCat.objects.get(user=request.user)
        form = UserCatForm(instance=initcat)
    #If not Load form with initial value
    except:
        default = Categories.objects.get(catName='Other')
        default = [default,]
        form = UserCatForm(initial={'user':request.user,
                                    'cats':default})
    return form

#View to load and validate registration form
def signup(request):
    if request.method == 'POST':
        #Figure out which button was pressed
        #Options: add_income, add_expense, edit_item, delete_item
        if request.POST.get("submit"):
            form = UserCreateForm(request.POST)
            if form.is_valid():
                userid = form.save()
                #Log user in
                username = request.POST['username']
                password = request.POST['password1']
                user_obj = authenticate(username=username, password=password)
                #Create UserCat Object and add default cat of Other
                default = Categories.objects.get(catName='Other')
                usercat = UserCat(user=userid)
                usercat.save()
                usercat.cats.add(default)
                #Log user in and redirect to home page
                if user_obj.is_active:
                    login(request, user_obj)
                    # Redirect to a success page.
                    return redirect('home')
                #else - Disabled Account would go here
            #Registration Form Invalid    
            else:
                temp = 'register.html'
                footer = 'New User'
                c = {'footer': footer,'form': form}
                return render(request, temp, c)
    else:
        form = UserCreateForm()
        temp = 'register.html'
        footer = 'New User'
        c = {'footer': footer,
             'form': form}
        return render(request, temp, c)


#View to hold account management
@login_required
def account_mgmt(request):
    if request.method == 'POST':
        account_mgmt_btn = request.POST.get("account_mgmt_btn")
        #Button Options
        #save_form.Meta.name - Get Form Name and save
        if account_mgmt_btn == "Save User Categories":
            #If object exists for user update
            try:
                initcat = UserCat.objects.get(user=request.user)
                form = UserCatForm(request.POST, instance=initcat)
            #If not create one
            except:
                form = UserCatForm(request.POST)
            if form.is_valid():
                form.save()
                form = ''
                footer = ''
                #Variable to display menu buttons
                is_get = True
            #No Categories Selected
            else:
                footer = ''
                is_get = False            

            #Test if call came from ExpensesForm
            if request.POST['formdata']:
                temp = 'config.html'
                form = expensesformload(request)
                footer = 'Categories Updated'
                c = {'itemtype': 'Expense',
                     'form': form,
                     'footer': footer}
                
            #Called from /settings
            else:
                temp = 'manage.html'  
                c = {'is_get': is_get,
                     'form': form,
                     'footer':footer}
            return render(request, temp, c)

        #Save button on User Profile Form
        elif account_mgmt_btn == "Save User Profile":
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                form = ""
                footer = "Profile Updated"
                #Variable to display menu buttons
                is_get = True
            #Invalid Form Selected
            else:
                footer = "Edit Your Profile"
                is_get = False            
                    
            temp = 'manage.html'  
            c = {'is_get': is_get,
                 'form': form,
                 'footer':footer}
            return render(request, temp, c)

        #Save button on User Profile Form
        elif account_mgmt_btn == "Save Category":
            form = CategoriesForm(request.POST)
            if form.is_valid():
                cat = form.save()
                #Add Category to user cats
                usercat = UserCat.objects.get(user=request.user)
                usercat.cats.add(cat)
                footer = 'Category Added'
                #If formdata exist, call came from ExpensesForm
                if request.POST['formdata']:
                    form = expensesformload(request, category=cat)
                    temp = 'config.html'
                    footer = 'Categories Updated'
                    c = {'itemtype': 'Expense',
                         'form': form,
                         'footer': footer}
                else:
                    temp = 'manage.html'  
                    #Load UserCatForm
                    #Try and get UserCat object for user
                    try:
                        initcat = UserCat.objects.get(user=request.user)
                        form = UserCatForm(instance=initcat)
                    #If not Load form with initial value
                    except:
                        default = Categories.objects.get(catName='Other')
                        default = [default,]
                        form = UserCatForm(initial={'user':request.user,
                                                    'cats':default})
                    c = {'form': form,'footer':footer}
                    
            else:
                footer = 'Form Invalid'
                
            #Render form with context
            return render(request, temp, c)

        #Add Category Button
        elif account_mgmt_btn == "Add Category":
            form = CategoriesForm()
            footer = 'Add Category'
            temp = 'manage.html'  
            c = {'form': form,'footer':footer}
            if request.POST.get('formdata'):
                nextform = request.POST.get('formdata')
                c = {'form': form,'footer':footer, 'nextform':nextform}
            
            return render(request, temp, c)
            
        #Cancel - redirect back to this view
        elif account_mgmt_btn == "Cancel":
            temp = 'manage.html'
            footer = ''
            is_get = True
            c = {'is_get': is_get,
                 'footer':footer}
            #If formdata exist, call came from ExpensesForm
            if request.POST['formdata']:
                form = expensesformload(request)
                temp = 'config.html'
                footer = 'Categories Updated'
                c = {'itemtype': 'Expense',
                     'form': form,
                     'footer': footer}
            return render(request, temp, c)

        #Edit Profile button pressed
        elif account_mgmt_btn == "Edit Profile":
            #Load UserProfileForm
            form = UserProfileForm(instance=request.user)
            temp = "manage.html"
            footer = "Edit Your Profile"
            c = {'form': form,
                 'footer':footer}
            return render(request, temp, c)
        
        #Edit Categories Button Pressed
        elif account_mgmt_btn == "Edit Categories":
            #Load UserCatForm from custom function
            form = usercatformload(request)
            temp = 'manage.html'
            footer = 'Select Desired Expense Categories'
            c = {'form':form,
                 'footer':footer}
            return render(request, temp, c)
        
        #Delete Budget Button
        elif account_mgmt_btn == "Delete Budget":
            #Delete all Items with owner of user
            Items.objects.filter(user=request.user).delete()
            return redirect('home')
        
        #Delete Budget Button
        elif account_mgmt_btn == "Delete Account":
            #Delete all Items with owner of user
            username = request.user.username
            user = User.objects.get(username=username)
            user.delete()
            return redirect('logout')
        
        #Cancel back to home page
        elif account_mgmt_btn == "Home":
            return redirect('home')
        
        else:
            temp = 'manage.html'
            footer = 'This Feature is in Development!'
            c = {'footer':footer}
            return render(request, temp, c)
        
    #Accessed from link (GET)
    else:
        temp = 'manage.html'
        footer = ''
        #Variable to display menu buttons
        is_get = True
        c = {'is_get': is_get,
             'footer':footer}
        return render(request, temp, c)
    
    
#View to Add income and expenses
@login_required
def config(request):
    #uses config.html
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        #Grab button data
        config_btn = request.POST.get("config_btn")
        #Figure out which button was pressed

        #Add Income from home page
        if config_btn == "Add Income":
            #Render Income ModelForm
            footer = 'Adding Income'
            form = IncomeForm(initial={'itemType': 'income',
                                       'user': request.user})
            itemtype = 'Income'
            c = {'itemtype':itemtype,
                 'form':form,
                 'footer':footer,}
            return render(request, 'config.html', c)
        
        #Add Expense from home page
        elif config_btn == "Add Expense":
            #Render Expense ModelForm
            footer = 'Adding Expense'
            footer = type(request.user)
            itemtype = 'Expense'
            form = ExpensesForm(initial={'itemType': 'expense',
                                         'user': request.user},
                                userid=request.user)
            c = {'itemtype':itemtype,
                 'form':form,
                 'footer':footer,}
            return render(request, 'config.html', c)
        
        #Save Expense 
        elif config_btn == "Save Expense":
            form = ExpensesForm(request.POST, userid=request.user)
            if form.is_valid():
                form.save()
                return redirect('home')
            else:
                temp = 'config.html'     
                footer = 'Expense Form Invalid'
                c = {'form':form,'footer':footer,}
                return render(request, temp, c)
            
        #Save Income
        elif config_btn == "Save Income":
            form = IncomeForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('home')
            else:
                form = IncomeForm(request.POST)
                temp = 'config.html'     
                footer = 'Form Invalid'
                c = {'form':form,'footer':footer,}
                return render(request, temp, c)
            
        #Edit Categories Button Pressed on ExpensesForm
        #Name of button = view_name_btn
        elif config_btn == "edit_category":
            #Load UserCatForm
            form = usercatformload(request)
            #put request.post into dict and pass to template
            expensesform = request.POST
            temp = 'manage.html'
            footer = 'Select desired categories'
            c = {'form':form,
                 'nextform': expensesform,
                 'footer':footer}
            return render(request, temp, c)
        
        #Cancel Button    
        else:
            return redirect('home')

    # if a GET (or any other method) we'll create a blank form
    else:
        footer = 'GET request'
        c = {'footer':footer,}
        return render(request, 'config.html', c)

    
#Home view - displays budget    
@login_required
def home(request):
    #Check is highest effective date in BudgetData is lower than
    #Desired Budget End Date, if so run UpdateData
    #Plug Beginning and End Times into Build to display only data user wants
    footer = '* Line item modified'
    Budget.update_data(request.user,budget_len=12)
    lineitems = Budget.build(request.user, historical_length=3)
    c = {'lineitems': lineitems,
         'footer':footer,}
    return render(request, 'home.html', c)

#View to edit budget line items
@login_required
def edit(request, item_id):
    if request.method == 'POST':
    #Update button on on edititem.html EditForm
        edit_btn = request.POST.get("edit_btn")
        if edit_btn == "Update":
            item = BudgetData.objects.get(pk=item_id)
            init = {'itemAmmount':item.itemAmmount,
                    'itemNote':item.itemNote}
            form = EditForm(request.POST, initial=init)
            if form.is_valid():
                #If Nothing has changed redirect to /payplanner
                changed = form.changed_data
                if len(changed) < 2:
                    return redirect('home')
                #If something has changed call update_line(), redirect home
                else:
                    #Get Radio button value if present, if not assign single
                    try:
                        editopt = request.POST['edit_opt']
                    except:
                        editopt = 'single'
                    #If future radio button selected    
                    if editopt == 'future':
                        #Update current and future dates()
                        junk,bunk = Budget.update_future(item,request.POST)
                        footer = ('NEW:%s   -   OLD:%s' % (junk,bunk))
                    #If All button selected    
                    elif editopt == 'all':
                        Budget.update_all(item,request.POST)
                    #If single or not present (implied single) update line
                    else:
                        Budget.update_line(item,request.POST)
                  
                    #Redirect to home
                    return redirect('home')
            #Form Not Valid
            else:
                temp = 'edititem.html'
                name = item.parentItem.itemName.rstrip('*')
                notsingle = True
                if item.parentItem.payCycle.cycleName == 'Single':
                    notsingle = False
                footer = ('Edit %s' % name)
                c = {'itemid': item_id,
                     'name':name,
                     'notsingle':notsingle,
                     'form':form,
                     'footer':footer,}
                #Indent this when done with updating line items
                return render(request, temp, c)
            
        #Delete button on on edititem.html EditForm
        elif edit_btn == "Delete":
            item = BudgetData.objects.get(pk=item_id)
            #Get Radio button value if present, if not assign single
            try:
                editopt = request.POST['edit_opt']
            except:
                editopt = 'single'
            Budget.delete_item(item,editopt)
            return redirect('home')
        
        #Cancel, Any other POST request
        else:
            return redirect('home')
    #Get Request (First call from home page)    
    else:
        temp = 'edititem.html'
        item = BudgetData.objects.get(pk=item_id)
        #Test if request user owns item, if not redirect home
        if not request.user == item.parentItem.user:
            return redirect('home')
        notsingle = True
        if item.parentItem.payCycle.cycleName == 'Single':
            notsingle = False
        form = EditForm(instance=item)
        name = item.parentItem.itemName.rstrip('*')
        footer = ('Edit %s' % name)
        c = {'itemid': item_id,
             'name':name,
             'notsingle':notsingle,
             'form':form,
             'footer':footer,}
        return render(request, temp, c)

                
    
