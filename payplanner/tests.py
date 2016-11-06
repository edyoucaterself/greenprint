from django.test import TestCase
from django.contrib.auth.models import User

from payplanner.models import BudgetData, Items, BudgetProfile
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
class UpdateBudgetNewUser(TestCase):

    """Test update_budget function in various different scenarios"""

    fixtures = ['base.json',]
    
    def setUp(self):
        self.user = User.objects.get(username='freshuser')
        

    def test_update_data_no_items_no_force(self):
        """Run update_data as it would be on home call first login"""
        
        #Get settings from budget profile
        try:
            budgetprofile = BudgetProfile.objects.get(user=self.user)
            budlen = budgetprofile.budgetLength
            histlen = budgetprofile.histLength
        except BudgetProfile.DoesNotExist:
            budlen = 12
            histlen = 3
            
        status,message = Budget.update_data(request.user,budget_length=budlen)
        self.assertEqual(status, 1)
