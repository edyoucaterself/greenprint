from datetime import date
from random import randrange

from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Min, Max

from payplanner.models import BudgetData, Items, Cycles, BudgetProfile
from payplanner.budget import Budget

#Test Budget.update_data for various scenarios
"""
Test functions
 - Add income, expense of each pay cycle
 - Cycle for each should:
     -Create Item
     -update_data
     -modify note and amount on single,future double
     -Check if pattern is correct (dates and amounts)
     -Check running total
     -Report errors
"""
class UpdateBudget(TestCase):

    """ Test update_budget function in various different scenarios """

    fixtures = ['init_user.json', 'init_payplanner.json']

    @staticmethod
    def duplicate_check(self, lineitems):

        """  Check lineitems for duplicates """

        for d in lineitems:
            #Grab Date
            date = d['itemdate']
            found_dates = BudgetData.objects.filter(parentItem__user=self.testuser, effectiveDate=date)
            #If more than one occurance of date found throw exception
            try:
                self.assertEquals(found_dates.count(),1)
            except AssertionError:
                print("Duplicate Found!\n")
                for o in found_dates:
                    print("%s - %s - %s" % (o.parentItem.itemName,o.effectiveDate,o.itemAmmount))
            
                    
    @staticmethod
    def length_total_check(self, testparam, **kwargs):

        """Test if User Budget is correct length and total"""

        ##Notes:
        #Need to add check for double dates (seperate method)
        
        ##Grab test type from kwargs
        if 'test' in kwargs:
            testtype = kwargs['test']
        else:
            testtype = 'Initial Build'

        if 'no_update' in kwargs:
            no_update = kwargs['no_update']
        else:
            no_update = False
            
        #Set up variables
        status = False
        
        #Run update_data
        exitstat, exitmsg, addedmsg = ('Update Data Skipped...', 'Update Data Skipped...', 'Update Data Skipped...')    
        if not no_update:
            exitstat, exitmsg, addedmsg = Budget.update_data(self.testuser, force=True)

        #Build budget
        tstmsg, lineitems = Budget.build(self.testuser,test=True)
        budgetlen = len(lineitems) - 1
        
        #Get last item in budget
        item = lineitems[budgetlen]
        name = item['name']
        cycle = item['cycle']
        amount = item['amount']
        running_total = item['running_total']

        #compare total to rtotaldct
        testtotal = testparam[testtype]
        message = ("Cycle: %s\tUpdate Type: %s\tRunning Total: %s\tPassing Values: %s" % (cycle.cycleName, testtype, running_total, testtotal))
        try:
            self.assertIn(abs(running_total),testtotal, message)
        except AssertionError:
            print("FAILED\n%s" % message)
            c = 1
            for w in lineitems:
                print("%s:%s:%s:%s:%s:%s" % (c, w['parent'], w['itemdate'], w['name'],w['amount'],w['running_total']))
                c += 1
        
        return addedmsg, budgetlen, status, lineitems

    def test_pay_cycles(self):
        
        """ Test each paycycle """

        self.testuser = User.objects.get(username='freshuser')
        cycles = Cycles.objects.all()
        types = ['income', 'expense']

        #Dictionary to hold test values
        testparamdct = {'Single': {'Initial Build': [1000,],  "Update All": [1500,], "Update Single": [2000,], "Update Future": [2000,2000]},
                        'Weekly': {'Initial Build': [53000,], "Update All": [79500,], "Update Single": [80000,], "Update Future": [129000,128000]},
                        'Bi-Weekly': {'Initial Build': [27000,], "Update All": [40500,], "Update Single": [41000,], "Update Future": [63000, 64000]},
                        'Monthly': {'Initial Build': [12000,], "Update All": [18000,], "Update Single": [18500,], "Update Future": [24000,25000,26500]},
                        'Quarterly': {'Initial Build': [4000,], "Update All": [6000,], "Update Single": [6500,], "Update Future": [9500,]},
                        'Annual': {'Initial Build': [1000,], "Update All": [1500,], "Update Single": [2000,], "Update Future": [0,]},
                        'Semi-Monthly 1st/15th': {'Initial Build': [24000,], "Update All": [36000,], "Update Single": [36500,], "Update Future": [55000,54000,56500]},
                        'Semi-Monthly 15th/Last': {'Initial Build': [24000,], "Update All": [36000,], "Update Single": [36500.], "Update Future": [55500,56500]},
                        }
        
        for i in cycles:
            for itemtype in types:
                name = ("%s - %s" % (i.cycleName, itemtype))
                #Create Item
                newitem = Items.objects.create(user=self.testuser,
                                               itemName=name,
                                               itemType=itemtype,
                                               category="UpdateBudget Test",
                                               itemAmount=1000,
                                               payCycle=i,
                                               nextDueDate=date.today())
                #Test item creation
                testparam = testparamdct[i.cycleName]
                addedmsg, budgetlen, status, lineitems = UpdateBudget.length_total_check(self, testparam, test="Initial Build")

                #Test for duplicates
                self.duplicate_check(self, lineitems)
                
                #If Line items is only 1 item, cotinue to next cycle
                if len(lineitems) == 1:
                    BudgetData.objects.filter(parentItem=newitem).delete()
                    Items.objects.filter(user=self.testuser).delete()
                    continue
                
                #Create objects and information for updates
                line = BudgetData.objects.filter(parentItem__user=self.testuser).order_by("?").first()
                parent = line.parentItem.id
                newdata = {"parentItem": parent, "itemAmmount":1500, "itemNote":"All Items Update"}

                #Call update_all(item object, new data dict)
                new_par = Budget.update_all(line, newdata)
                    
                #Test if BudgetData is correct length and total
                testparam = testparamdct[i.cycleName]    
                addedmsg, budgetlen, status, lineitems = UpdateBudget.length_total_check(self, testparam, test="Update All")

                #Test for duplicates
                self.duplicate_check(self, lineitems)    
                #Call update_line(item object, new data dict)
                line = BudgetData.objects.filter(parentItem__user=self.testuser).order_by("?").first()
                newdata['itemAmmount'] += 500
                Budget.update_line(line, newdata)
                addedmsg, budgetlen, status, lineitems = UpdateBudget.length_total_check(self, testparam, test="Update Single")

                #Test for duplicates
                self.duplicate_check(self, lineitems)
                #Call update_future(item object, new data dict) on first object, unless its single, than choose second
                line_items = BudgetData.objects.filter(parentItem__user=self.testuser).order_by('effectiveDate')
                c = 1
                if len(line_items) < 5:
                    line = line_items[0]
                else:
                    line = line_items[4]
    
                #Random Line
                #line = BudgetData.objects.filter(parentItem__user=testuser).order_by("?").first()
                newdata['itemAmmount'] += 500
                newpar,oldpar = Budget.update_future(line, newdata)
                #Test if BudgetData is correct length and total
                addedmsg, budgetlen, status, lineitems = UpdateBudget.length_total_check(self, testparam, test="Update Future")

                #Test for duplicates
                self.duplicate_check(self, lineitems)
                #Erase item and budgetdata
                BudgetData.objects.filter(parentItem=newitem).delete()
                Items.objects.filter(user=self.testuser).delete()
