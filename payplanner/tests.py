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
    def rand_item(testuser, budgetlen):

        """ Function to return random itemid for specified user """
        
                #Create new single, future and all items
        #If not single pick random line
        if budgetlen != 0:    
            #Pick random number within range and grab item
            min_id = BudgetData.objects.filter(parentItem__user=testuser).aggregate(Min('id'))
            max_id = BudgetData.objects.filter(parentItem__user=testuser).aggregate(Max('id'))
            item_id = randrange(min_id['id__min'],max_id['id__max'])
        else:
            item_id = BudgetData.objects.filter(parentItem__user=testuser).values_list('id')
            item_id = item_id[0]
            item_id = item_id[0]
        line = BudgetData.objects.get(pk=item_id)
        return line
    
    @staticmethod
    def length_total_check(testuser,testparam, **kwargs):

        """Test if User Budget is correct length and total"""
        
        ##Grab test type from kwargs
        if 'test' in kwargs:
            testtype = kwargs['test']
        else:
            testtype = 'Initial Build'

        if 'no_update' in kwargs:
            no_update = kwargs['no_update']
        else:
            no_update = False
            
        ##Outputs - Pass/Fail correct length and total
        
        #Run update_data
        exitstat, exitmsg, addedmsg = ('Update Data Skipped...', 'Update Data Skipped...', 'Update Data Skipped...')    
        if not no_update:
            exitstat, exitmsg, addedmsg = Budget.update_data(testuser, force=True)

        #Build budget
        tstmsg, lineitems = Budget.build(testuser,test=True)
        budgetlen = len(lineitems) - 1
        #Get last item in budget
        item = lineitems[budgetlen]
        name = item['name']
        cycle = item['cycle']
        amount = item['amount']
        running_total = item['running_total']

        #compare total to rtotaldct
        testtotal = testparam[testtype]
        #Get absolute value
        running_total = abs(running_total)
        testtotal = abs(testtotal)
        #print("TEST %s: %s" % (cycle.cycleName,running_total))
        
        if running_total == testtotal:
            print("%s Passed: %s %s Test: %s == %s" % (testtype, cycle.cycleName, name, running_total, testtotal))
            status = True
        else:
            beg_date, end_date = tstmsg
            print("%s Failed: %s %s Test: %s != %s" % (testtype, cycle.cycleName, name, running_total, testtotal))
            status = False

        return addedmsg, budgetlen, status, lineitems

    def test_pay_cycles(self):
        
        """ Test each paycycle """

        testuser = User.objects.get(username='freshuser')
        cycles = Cycles.objects.all()
        types = ['income', 'expense']

        #Dictionary to hold test values
        testparamdct = {'Single': {'Initial Build': 1000,  "Update All": 1500, "Update Single": 2000},
                        'Weekly': {'Initial Build': 53000, "Update All": 79500, "Update Single": 80000},
                        'Bi-Weekly': {'Initial Build': 27000, "Update All": 40500, "Update Single": 41000},
                        'Monthly': {'Initial Build': 12000, "Update All": 18000, "Update Single": 18500},
                        'Quarterly': {'Initial Build': 4000, "Update All": 6000, "Update Single": 6500},
                        'Annual': {'Initial Build': 1000, "Update All": 1500, "Update Single": 2000},
                        'Semi-Monthly 1st/15th': {'Initial Build': 24000, "Update All": 36000, "Update Single": 36500},
                        'Semi-Monthly 15th/Last': {'Initial Build': 24000, "Update All": 36000, "Update Single": 36500},
                        }
        print("------------------------------------------------------------")
        
        for i in cycles:
            for itemtype in types:
                name = ("%s - %s" % (i.cycleName, itemtype))
                #Create Item
                newitem = Items.objects.create(user=testuser,
                                               itemName=name,
                                               itemType=itemtype,
                                               category="UpdateBudget Test",
                                               itemAmount=1000,
                                               payCycle=i,
                                               nextDueDate=date.today())
                #Test item creation
                testparam = testparamdct[i.cycleName]
                addedmsg, budgetlen, status, lineitems = UpdateBudget.length_total_check(testuser, testparam, test="Initial Build")

                #Create objects and information for updates
                line = UpdateBudget.rand_item(testuser, budgetlen)
                parent = line.parentItem.id
                newdata = {"parentItem": parent, "itemAmmount":1500, "itemNote":"All Items Update"}
                
                #Call update_all(item object, new data dict)
                new_par = Budget.update_all(line, newdata)
                    
                #Test if BudgetData is correct length and total
                testparam = testparamdct[i.cycleName]    
                addedmsg, budgetlen, status, lineitems = UpdateBudget.length_total_check(testuser, testparam, test="Update All")
                    
                #Call update_line(item object, new data dict)
                line = UpdateBudget.rand_item(testuser, budgetlen)
                newdata['itemAmmount'] += 500
                Budget.update_line(line, newdata)
                addedmsg, budgetlen, status, lineitems = UpdateBudget.length_total_check(testuser, testparam, test="Update Single")
                '''
                for w in addedmsg:
                    print(w)
                for w in lineitems:
                    print("%s:%s:%s:%s" % (w['itemdate'], w['name'],w['amount'],w['running_total']))
                '''

                #Call update_future(item object, new data dict)

                #Test if BudgetData is correct length and total

                #Erase item and budgetdata
                BudgetData.objects.filter(parentItem=newitem).delete()
                Items.objects.filter(user=testuser).delete()
                print("------------------------------------------------------------")
