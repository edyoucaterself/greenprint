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

    def test_pay_cycles(self):
        
        """ Test each paycycle """

        testuser = User.objects.get(username='freshuser')
        cycles = Cycles.objects.all()
        types = ['income', 'expense']

        #Dictionary to hold test values
        rtotaldct = {'Single': 1000,
                     'Weekly': 52000,
                     'Bi-Weekly': 26000,
                     'Monthly': 12000,
                     'Quarterly': 4000,
                     'Annual': 1000,
                     'Semi-Monthly 1st/15th': 24000,
                     'Semi-Monthly 15th/Last': 24000
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
                #Run update_data
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
                #Add try clause incase of mismatch
                #Test distance from 0 (absolute value?)
                if itemtype == 'expense':
                    testtotal = rtotaldct[cycle.cycleName] * -1
                else:
                    testtotal = rtotaldct[cycle.cycleName]

                #Get absolute value
                running_total = abs(running_total)
                testtotal = abs(testtotal)
                if running_total >= testtotal:
                    print("Cycle Build Passed: %s" % name)
                else:
                    beg_date, end_date = tstmsg
                    print("Cycle Build Failed: Name:%s\tTest Total:%s\tRunning Total:%s\tBeg. Date:%s\tEnd Date:%s\tExit Msg:%s" % (name, testtotal, running_total, beg_date, end_date, exitmsg))
                    x = len(addedmsg)
                    for m in addedmsg:
                        print(m)
                    """
                    for li in lineitems:
                        j = li['name']
                        k = li['itemdate']
                        l = li['amount']
                        m = li['running_total']
                        print("%s:%s:%s:%s" % (j,k,l,m))
                    """

                

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

                #Create object and information for update
                all_line = BudgetData.objects.get(pk=item_id)
                all_parent = all_line.parentItem.id
                all_newdata = {"parentItem": all_parent, "itemAmmount":1500, "itemNote":"All Items Update"}
                
                #Call update_all(item object, new data dict)
                new_par = Budget.update_all(all_line, all_newdata)

                #Test difference, should be 500
                if new_par.itemAmount - all_line.itemAmmount != 500:
                    print("Update All Failed on item %s" % all_line)
                else:
                    print("Update All Succeeced on item %s" % all_line)
                #Test if BudgetData is correct length and total
                
                #Call update_line(item object, new data dict)

                #Test if BudgetData is correct length and total

                #Call update_future(item object, new data dict)

                #Test if BudgetData is correct length and total

                #Erase item and budgetdata
                BudgetData.objects.filter(parentItem=newitem).delete()
                Items.objects.filter(user=testuser).delete()
                print("------------------------------------------------------------")
