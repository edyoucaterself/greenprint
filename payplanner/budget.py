#budget.py
#Created By: Matt Agresta
#Created On: 9/07/2016

#Set up Environment
import json
from datetime import date
from dateutil.relativedelta import relativedelta

from django.db.models import Max

from .models import Items, BudgetData, Cycles


class Budget():

    """ Controls BudgetData via Items tables """
    #Function to serialize date list to json
    #Returns str of serialized data
    @staticmethod
    def date_to_json(skiplst):
        #Go through each date in list and convert to dict
        date_list = []
        if skiplst is None or len(skiplst) < 1:
            return date_list
        for d in skiplst:
            mydict = {'y':d.year,'m':d.month,'d':d.day}
            date_list.append(mydict)
        date_str = json.dumps(date_list)
        return date_str
    
    #Function to deserialize date string
    #Returns list of datetime objects
    @staticmethod
    def json_to_date(datestr):
        date_list = []
        #Test if datestr is empty or None, if so return empty list
        if datestr is None or len(datestr) < 1:
            return date_list
        jsonDec = json.decoder.JSONDecoder()
        jlist = jsonDec.decode(datestr)
        for a in jlist:
            x = date(a['y'],a['m'],a['d'])
            date_list.append(x)
        return date_list
    #Function to Delete Budget Items/Data
    @staticmethod
    def delete_item(line, opt):
        #line = BudgetData object
        #opt = edit_opt
        parItem = line.parentItem
        #Single Line - Add Data to Skip Line, Remove Single BudgetData row
        if opt == 'single':
            #Remove Line
            line.delete()
            cycle = parItem.payCycle.cycleName
            #Add Date to Items.skipDate
            skipdate = Budget.json_to_date(parItem.skiplst)
            #If its not a single item and not in skip list, add
            if not line.effectiveDate in skipdate and cycle != 'Single':
                skipdate.append(line.effectiveDate)
                datestr = Budget.date_to_json(skipdate)
                parItem.skiplst = datestr
                parItem.save()
            #If it is a single item, just delete the parent and row
            else:
                parItem.delete()
        #All Lines   - Delete Parent Item, all BudgetData 
        elif opt == 'all':
            BudgetData.objects.filter(parentItem=parItem).delete()
            parItem.delete()
        #Future Lines- Add End Date to Item, Remove All BudgetData rows
        else:
            BudgetData.objects.filter(parentItem=parItem).delete()
            cyclength = parItem.payCycle.cycleLength
            cycle = relativedelta(days=cyclength)
            enddate = (line.effectiveDate - cycle)
            parItem.endDate = enddate
            parItem.save()

    #Function to update all budgetdata lines
    @staticmethod
    def update_all(line,newdata):
        #Remove all budgetdata lines with parent
        a = newdata['parentItem']
        parItem = Items.objects.get(pk=newdata['parentItem'])
        BudgetData.objects.filter(parentItem = parItem).delete()
        #Update parent item
        parItem.itemAmount = newdata['itemAmmount']
        parItem.itemNote = newdata['itemNote']
        parItem.save()
        
    #Function to update BudgetData Future Rows
    @staticmethod
    def update_future(line,newdata):
        #Add End Date to Parent Item
        a = newdata['parentItem']
        parItem = Items.objects.get(pk=newdata['parentItem'])
        #Copy parent to new parent
        newparent = parItem
        #Remove All BudgetData rows of old parent and current line
        BudgetData.objects.filter(parentItem = parItem).delete()
        #Modify Old Parent
        cyclength = parItem.payCycle.cycleLength
        cycle = relativedelta(days=cyclength)
        enddate = (line.effectiveDate - cycle)
        parItem.endDate = enddate
        parItem.save()
        #Modify New Parent
        newparent.id = None
        newparent.nextDueDate = line.effectiveDate
        newparent.itemName = ('%s*' % parItem.itemName)
        newparent.itemAmount = newdata['itemAmmount']
        newparent.itemNote = newdata['itemNote']
        newparent.endDate = None
        newparent.save()
        line.delete()
        return type(newparent),type(parItem)
    
    #Function to update BudgetData line item
    @staticmethod
    def update_line(line, newdata):
        #Get Parent Item
        a = newdata['parentItem']
        parItem = Items.objects.get(pk=newdata['parentItem'])
        cycle = parItem.payCycle.cycleName
        
        #Add Date to Items.skipDate
        skipdate = Budget.json_to_date(parItem.skiplst)
        if not line.effectiveDate in skipdate and cycle != 'Single':
            skipdate.append(line.effectiveDate)
            datestr = Budget.date_to_json(skipdate)
            parItem.skiplst = datestr
            parItem.save()
        #Edit New parentItem - Only if parItem.cycleName.cycleName is not Single
        if cycle != 'Single':
            #Create parent copy
            newparent = parItem
            newparent.pk = None
            newparent.itemName = ('%s*' % newparent.itemName)
            newparent.itemAmount = newdata['itemAmmount']
            single = Cycles.objects.get(cycleName='Single')
            newparent.payCycle = single
            newparent.skiplst = None
            newparent.nextDueDate = line.effectiveDate
            newparent.save()
            line.parentItem = newparent
        #If single entry, modify the parent item
        else:
            parItem.itemAmount = newdata['itemAmmount']
            parItem.itemNote = newdata['itemNote']
            parItem.save()
        
        #Alter BudgetData row: parentItem(newly created above), itemAmmount(from newdata)
        line.itemAmmount = newdata['itemAmmount']
        line.itemNote = newdata['itemNote']
        line.save()

    
    #Method to build budget with Budget Data
    @staticmethod
    def build(username, **kwargs):
        #Grab all items from BudgetData and sort by date and then income/expense
        itemlst = BudgetData.objects.values().filter(parentItem__user=username).order_by('effectiveDate','-parentItem__itemType')
        running_total = 0
        budget_output = []
        linenum = 1
        today = date.today()
        #Check for historical length (in weeks)
        if 'historical_length' in kwargs:
            w = kwargs['historical_length']
            tlength = relativedelta(weeks=w)
        else:
            tlength = relativedelta(weeks=2)
        beg_date = today - tlength

        #Check for budget length (in months)
        if 'budget_length' in kwargs:
            m = kwargs['budget_length']
            tlength = relativedelta(months=m)
        else:
            tlength = relativedelta(months=12)
        end_date = today + tlength
        
        for line in itemlst:
            item = BudgetData.objects.get(pk=line['id'])
            if item.effectiveDate < beg_date or item.effectiveDate > end_date:
                continue
            name = item.parentItem.itemName
            itemtype = item.parentItem.itemType
            amount = item.itemAmmount
            itemdate = item.effectiveDate
            itemid = item.id
            itemnote = item.itemNote
            if itemtype == 'income':
                running_total += amount
                isincome = True
            else:
                running_total -= amount
                isincome = False
            
            lineitem = (itemid,isincome,itemdate,name,amount,running_total,itemnote)
            budget_output.append(lineitem)
            #print('%s %s\t%s\t\t%s\t\t%s' % (linenum,itemdate,name,amount,running_total))
            linenum +=1
        return budget_output
    
    #Method to Add New items to budget
    @staticmethod
    def update_data(userid, **kwargs):
        #Grab force from keyword args
        if 'force' in kwargs:
            force = kwargs['force']
        else:
            force = False

        #Get End Date from kwargs
	if 'budget_len' in kwargs:
            m = kwargs['budget_len']
            yearlen = relativedelta(months=m)
        else:
            yearlen = relativedelta(months=12) 
        today = date.today()
	end_date = today + yearlen
	
	#Get last item in budget data and compare to end date
	maxdate = BudgetData.objects.filter(parentItem__user=userid).aggregate(Max('effectiveDate'))
	maxdate = maxdate['effectiveDate__max']
	if maxdate > end_date and force == False:
            exitmsg = []
            exitmsg.append('End Date: %s' % end_date)
            exitmsg.append('Max Date: %s' % maxdate)
            exitmsg.append('Nothing to Build')
            return exitmsg
        
	#Get Items to build BudgetData
	items = Items.objects.values().filter(user=userid)
	for budgetitem in items:
            #Create model object for item
            item = Items.objects.get(pk=budgetitem['id'])
            #Gather information about item
	    name = item.itemName
	    itemtype = item.itemType
	    amount = item.itemAmount
	    nextdue = item.nextDueDate
	    paycycle = item.payCycle.cycleName
	    itemenddate = item.endDate
	    itemnote = item.itemNote
	    skiplist = Budget.json_to_date(item.skiplst)
	    
	    
	    itemduedate = nextdue
	    #If single item, add and move on to next
	    if paycycle == 'Single':
                if not BudgetData.objects.values().filter(parentItem = item,effectiveDate = itemduedate):
                    data = BudgetData(parentItem = item, effectiveDate = itemduedate,itemAmmount = amount)
                    data.save()
                    print('Added %s: %s - %s - %s' % (name,itemduedate,amount,paycycle))
                    continue
                    
	    else:
                #If no end date specified create fake on that will always be greater then itemduedate
                if itemenddate is None:
                    itemenddate = date(9999,12,31)
	    	#Get cyclelength from Item
                cyclength = item.payCycle.cycleLength
                #Figure out timedelta based on cycle
                if paycycle == 'Monthly':
                    itemcycle = relativedelta(months=1)
                elif paycycle == 'Quarterly':
                    itemcycle = relativedelta(months=3)
                else:
                    itemcycle = relativedelta(days=cyclength)
	
                while itemduedate < end_date:
                    #Break loop, go to next item if due date is past budget end date
                    if itemduedate > itemenddate:
                            break
                    #If date is on skip list increase duedate and continue
                    if itemduedate in skiplist:
                        itemduedate += itemcycle
                        continue
                    #Write to BudgetData table if a matching item is not already found
                    if BudgetData.objects.values().filter(parentItem = item,effectiveDate = itemduedate):
                        itemduedate += itemcycle
                        continue
                    else:
                        #Need to Add itemNote - Don't want to add it for everyone, need to figure out how to delete with foreign keys and keep budget items
                        data = BudgetData(parentItem = item,
                                          effectiveDate = itemduedate,
                                          itemAmmount = amount,
                                          itemNote = itemnote)
                        data.save()
                        print('Added %s: %s - %s - %s' % (name,itemduedate,amount,paycycle))
                        itemduedate += itemcycle
                    
              
                    
				 
