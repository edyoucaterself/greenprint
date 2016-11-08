from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

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
        
                #Test if BudgetData is correct length and total
                budgetdata = BudgetData.objects.filter(parentItem=newitem)
                lineitems = Budget.build(testuser)
                budgetlen = len(lineitems) - 1
                item = lineitems[budgetlen]
                name = item['name']
                cycle = item['cycle']
                amount = item['amount']
                running_total = item['running_total']

                #compare total to rtotaldct
                if running_total == rtotaldct[cycle.cycleName]:
                    print("Cycle Passed: %s\t%s\t%s\t%s" % (name, cycle, amount, running_total))
                else:
                    print("Cycle Failed: %s\t%s\t%s\t%s" % (name, cycle, amount, running_total))

                print("------------------------------------------------------------")

                #Create new single, future and all items
                
                #Call update_line(item object, new data dict)

                #Test if BudgetData is correct length and total

                #Call update_future(item object, new data dict)

                #Test if BudgetData is correct length and total

                #Call update_all(item object, new data dict)

                #Test if BudgetData is correct length and total

                #Erase item and budgetdata
                BudgetData.objects.filter(parentItem=newitem).delete()
                Items.objects.filter(user=testuser).delete()
                
