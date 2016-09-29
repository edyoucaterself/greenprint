PayPlanner README

To Do list:

-Fix bug - Cancel button in config.html renders form errors instead of redirecting to home view. Works in dev.
-Fix bug - Any user can navigate to any budget item but entering /payplanner/config/nnnn - Where nnnn = BudgetItem.id
		-Shortterm - Top of view compare request.user to item.parentItem.user, if not  match return redirect('home')
		-Longterm - Create decerator to compare request.user and instance user (e.g instance user would be parentItem.user)

-Remove key in settings_dev, import settings_dev.py into settings.py (remove rest)

-Extend User object to include categories
	-models.py 
		- Create cust_user model, inheriting django.contrib.auth.models.User
		- Add field user_cat = ManyToMany(Categories,to_field='catName') to cust_user Class 
		- override Items.__init__ to dyanamically set Categories list to user_cat items
	-forms.py 
		- Change model for UserCreateForm to cust_user

-Add password reset link to sign-in page (should be in comments)
	- Test postfix config is working on server

-Create form for user to manage categories and add categories

-Improve Efficiency/Flow 
	-Eventually look into getting rid of parent items, build data on income/expense form submit
		-Would need composite key with name and date to manage editing multiple lines at once.
		-Not sure if it would be any more efficient.

	-views.py - call update_data under edititem and config, not home load

	-budget.py
		-Budget.update_data()
			-Add ability to pass multiple Items object to it, create BudgetData only for that object if they do not exist
		-Budget.update_line()
			-Replace parItem = Items.object.get(.... with parItem = line.parentItem -Should work the same and save a db call
			-Modify parItem (Already  Done), Update BudgetData row (Currently removes it)
		-Budget.update_future()
			-Replace parItem = Items.object.get(.... with parItem = line.parentItem -Should work the same and save a db call
			-Modify Item, Create New parent, Remove BudgetData with parentItem == parItem && effectiveDate > parItem.endDate,
				pass new parent to update_data 

		-Budget.update_all()
			-Replace parItem = Items.object.get(.... with parItem = line.parentItem -Should work the same and save a db call
			-ID what has changed and update all objects on a single line


		
		
