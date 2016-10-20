#Forms.py
# Created By: Matt Agresta
# Created On: 9/05/2016
# Holds classes for each payplanner model
#-----------------------------------------------------------#
from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Cycles(models.Model):
    
    """ Holds pay cycles e.g. Weekly, Bi-Weekly, Monthly """
    
    def __str__(self):
        return self.cycleName

    #Name of Cycle to be displayed on Input Forms
    cycleName = models.CharField(
         max_length=150,
         unique=True,
         verbose_name='Name'
    )

    
    #Cycle Duration
    cycleLength = models.IntegerField(
        verbose_name='Length of Cycle(Days)'
    )

    class Meta:
        
        verbose_name_plural = 'Pay Cycles'
        

class Categories(models.Model):

    """ Holds Expense Catgeory Information """
    
    def __str__(self):
        return self.catName
    
    #Name - To be displayed on Expense Input Form
    catName = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Category'
    )
    
    class Meta:
        
        verbose_name_plural = 'Expense/Income Categories'
        

class UserCat(models.Model):

    """ Holds List of Categories User would like on expenses form """
    
    user = models.OneToOneField(User)
    cats = models.ManyToManyField(Categories,
                                  verbose_name='Select Desired Categories')

    
class Items(models.Model):

    """ Holds Expense and Income information for user """
    
    def __str__(self):
        return self.itemName
    
    #User who owns item
    user = models.ForeignKey(User)
    
    #Item Name Ex. Car Payment
    itemName = models.CharField(
         max_length=150,
         verbose_name='Name'
    )
    
    #Item type (expense or income)
    itemType = models.CharField(
        max_length=20,
        blank=True,
        verbose_name = 'Item Type'
    )
    
    #Category of item
    category = models.CharField(
        max_length=100,
        help_text='See Account Settings to modify choices!',
        null=True,
        blank=True,
    )
    
    #Ammount Due Ex 9999.99
    itemAmount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Amount'
    )
    
    #How Often expense is paid Ex One Time Only, Weekly, Monthly, Quarterly
    payCycle = models.ForeignKey(
        Cycles,
        to_field='cycleName',
        verbose_name='Pay Cycle',
    )
    
    #Hold day of the month expense is due
    nextDueDate = models.DateField(
        default=date.today,
        verbose_name='Next Due Date',
    )
    
    #Hold end date of expense, not required.
    #Used if Expense is paid off, Ammount Changes
    endDate = models.DateField(
        blank=True,
        null=True,
        verbose_name='End Date (optional)',
    )

    #Holds serialize json representing date objects
    skiplst = models.TextField(
        blank=True,
        null=True,
    )
    
    #Holds Notes on expense. Ex. Account Number, Event description
    itemNote = models.CharField(
         max_length=400,
         blank=True,
         verbose_name='Notes (optional)'
    )
    
    class Meta:
        
        verbose_name_plural = 'Income/Expenses'
        


class BudgetData(models.Model):

    """ Holds line items for budget """
    
    def __str__(self):
        display = ('%s %s' % (self.parentItem.itemName,self.effectiveDate))
        return display

    #Item object used to create line
    parentItem = models.ForeignKey(
        Items,
    )

    #Amount of line item
    itemAmmount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Amount'
    )
    #Hold effective date item
    effectiveDate = models.DateField(
        default=date.today,
    )

    #Any additional information for line item
    itemNote = models.CharField(
         max_length=400,
         blank=True,
         verbose_name='Notes'
    )

    class Meta:
        
        verbose_name_plural = 'Budget Data'


class BudgetProfile(models.Model):

    """ Holds settings for budget display """
    
    user = models.OneToOneField(User)
    
    budgetLength = models.IntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(1)],
        verbose_name='Budget Length (Months)')
    
    histLength = models.IntegerField(
        validators=[MaxValueValidator(52), MinValueValidator(1)],
        verbose_name='Historical Length (Weeks)')
