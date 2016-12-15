#budget.py
#Created By: Matt Agresta
#Created On: 9/07/2016

#Set up Environment
import json
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from calendar import HTMLCalendar
from calendar import monthrange

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

        """Update all budgetdata items with line parentItem """
        
        a = newdata['parentItem']
        parItem = Items.objects.get(pk=newdata['parentItem'])
        BudgetData.objects.filter(parentItem = parItem).delete()
        #Update parent item
        parItem.itemAmount = newdata['itemAmmount']
        parItem.itemNote = newdata['itemNote']
        parItem.save()
        return parItem
        
    #Function to update BudgetData Future Rows
    @staticmethod
    def update_future(line,newdata):

        """ Update item from certain date and on """
        #Monthly, Semi Monthly 1st/15 not starting at current line

        #Add End Date to Parent Item
        parItem = Items.objects.get(pk=newdata['parentItem'])
        #Copy parent to new parent
        newparent = parItem
        #Remove All BudgetData rows of old parent 
        a = BudgetData.objects.filter(parentItem = parItem).delete()
        a = BudgetData.objects.filter(parentItem = parItem)
        #Get paycycle from parent
        paycycle = parItem.payCycle.cycleName
        
        #Modify Old Parent
        #If cycle is semi monthly figure out pattern, day and create end date
        if re.match('Semi-Monthly', paycycle):
            #Get effectiveDate 
            effDate = line.effectiveDate
            #Get semi monthly pattern
            cycle,pattern = paycycle.split()
            if effDate.month != 1:
                prevmonth = effDate.month - 1
            else:
                prevmonth = 12
            
            #if the pattern is last
            if re.search('Last', pattern):
                #If effectiveDate.day = 15, get last day of last month
                if effDate.day == 15:
                    first,last = monthrange(effDate.year, effDate.month)
                    enddate = effDate.replace(month=prevmonth)
                    enddate = enddate.replace(day=last)
                #else set enddate.day to 15
                else:
                    enddate = effDate.replace(day=15)
                    
            else:
                #If effectiveDate.day = 15, set enddate.day to 1
                if effDate.day == 15:
                    enddate = effDate.replace(day=1)
                #else set enddate.day to 15 of last month
                else:
                    enddate = effDate.replace(month=prevmonth)
                    enddate = enddate.replace(day=1)
            
        else:        
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
        return newparent, parItem
    
    #Function to update BudgetData line item
    @staticmethod
    def update_line(line, newdata):
        
        #Get Parent Item
        a = newdata['parentItem']
        parItem = Items.objects.get(pk=newdata['parentItem'])
        cycle = parItem.payCycle.cycleName

        #Delete line
        del_item = line.delete()
        
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
        #kwarg month should be tuple (month,year)
        if 'month' in kwargs:
            month,year = kwargs['month']
            itemlst = BudgetData.objects.values().filter(parentItem__user=username,
                                                         effectiveDate__month=month,
                                                         effectiveDate__year=year).order_by('effectiveDate','-parentItem__itemType')
        else:
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
            
            #Get itemnote from item or parent add prefix if found
            if item.itemNote == '' and item.parentItem.itemNote != '':
                itemnote = item.parentItem.itemNote
            else:
                itemnote = item.itemNote

            #Adjust Total    
            if itemtype == 'income':
                running_total += amount
                isincome = True
            else:
                running_total -= amount
                isincome = False
            
            #lineitem = (itemid,isincome,itemdate,name,amount,running_total,itemnote)
            lineitem = {'istoday': item.is_today,
                        'cycle':item.parentItem.payCycle,
                        'parent': item.parentItem.id,
                        'itemid':itemid,
                        'isincome':isincome,
                        'itemdate':itemdate,
                        'name':name,
                        'amount':amount,
                        'running_total':running_total,
                        'itemnote':itemnote}
            budget_output.append(lineitem)
            #print('%s %s\t%s\t\t%s\t\t%s' % (linenum,itemdate,name,amount,running_total))
            linenum +=1

        if 'test' in kwargs:
            tstmsg = (beg_date, end_date)
            return tstmsg, budget_output
        else:
            return budget_output


    #Method to update semi monthly data
    @staticmethod
    def update_semi_monthly(item, budgetlength, **kwargs):

        """Updated semi monthly budget data - defaults to 15/last pattern """
        #List of exit messages
        exitmsg = []
        #get pattern from kwargs, set day
        if 'pattern' in kwargs:
            pattern = kwargs['pattern']
        else:
            pattern = 'last'

        #Get data from item
        name = item.itemName
        itemduedate = item.nextDueDate
        amount = item.itemAmount
        paycycle = item.payCycle.cycleName
        skiplist = Budget.json_to_date(item.skiplst)
        startmonth = itemduedate.month
        year = itemduedate.year

        if item.endDate is None:
            enddate = date(9999, 12, 25)
        else:
            enddate = item.endDate
        #for each month in budget length
        i = 0
        month = startmonth
        while i <= (budgetlength):
            #Get date pattern
            if pattern == 'last':
                first,sec = monthrange(year, month)
                first = 15
            else:
                first = 1
                sec = 15
               
            #Build budgetdata object for each day pattern    
            for d in first,sec:
                #Create date object based on month and pattern
                adjusteddate = date(year, month, d)

                #If date is on skip list increase duedate and continue
                if adjusteddate in skiplist:
                    #print("Skip Date Found for %s %s %s" % (name,amount,adjusteddate))
                    continue
                
                #Adjusted date needs to be greater than itemduedate and less than enddate
                if adjusteddate < itemduedate or adjusteddate > enddate:
                    continue
            
                #Test if object exists
                if not BudgetData.objects.values().filter(parentItem = item,effectiveDate = adjusteddate):
                    data = BudgetData(parentItem = item, effectiveDate = adjusteddate,itemAmmount = amount)
                    data.save()
                    exitmsg.append('Added %s: %s: %s - %s - %s' % (data.id, name,adjusteddate,amount,paycycle))

            #Increment Months and Counter
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            i +=1
            
        return exitmsg
        
    #Method to Add New items to budget
    @staticmethod
    def update_data(userid, **kwargs):
        exitmsg = []
        addedmsg = []
        #exit status
        #1 - Nothing to Build
        #0 - Items Added
        #2 - Error/Not Run Properly
        exitstatus = 2
        #Grab force from keyword args
        #force overrides maxdate comparison
        # Use after adding new Item
        if 'force' in kwargs:
            force = kwargs['force']
        else:
            force = False
        #Something obout this not working
            
        #Get End Date from kwargs
	if 'budget_length' in kwargs:
            budget_length = kwargs['budget_length']
        else:
            budget_length = 12

        yearlen = relativedelta(months=budget_length)
        today = date.today()
	end_date = today + yearlen
	
	#Get last item in budget data 
	budgetdata = BudgetData.objects.filter(parentItem__user=userid).annotate(Max('effectiveDate'))
        maxline = budgetdata.last()
        #If no BudgetData set max date to today to exit method
	if maxline is None:
            maxdate = date.today()
        else:
            maxdate = maxline.effectiveDate
            #Get Cycle Length
            cycle = maxline.parentItem.payCycle
            if cycle.cycleName == 'Single':
                linecycle = relativedelta(months=1)
            elif cycle.cycleName == 'Monthly':
                linecycle = relativedelta(months=1)
            elif cycle.cycleName == 'Quarterly':
                linecycle = relativedelta(months=3)
            else:
                linecycle = relativedelta(days=cycle.cycleLength)
            exitmsg.append('Max Line Cycle: %s' % linecycle)
            maxdate += linecycle
        
        exitmsg.append('End Date: %s' % end_date)
        exitmsg.append('Max Date: %s' % maxdate)
        exitmsg.append('Force: %s' % force)   
	if maxdate >= end_date and force == False:
            exitstatus = 1
            exitmsg.append('Nothing New to Build')
            return exitstatus, exitmsg
        
	#Get Items to build BudgetData, if empty, exit
	items = Items.objects.values().filter(user=userid)
	if len(items) is 0:
            exitstatus = 1
            exitmsg.append('No Items to build from')
            
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
                    exitstatus = 0
                    addedmsg.append('Added %s: %s - %s - %s' % (name,itemduedate,amount,paycycle))
                    continue
                
            #Semi Monthly cycle, needs special attention    
            elif re.match('Semi-Monthly', paycycle):
                #Get semi monthly pattern
                cycle,pattern = paycycle.split()
                #Call update_semi_monthly with pattern
                if re.search('Last', pattern):
                    msg = Budget.update_semi_monthly(item, budget_length)
                else:
                    msg = Budget.update_semi_monthly(item, budget_length, pattern="first")
                addedmsg.append(msg)
                continue
            
            #Reoccuring line item, cycle through till budget end        
	    else:
                #If no end date specified create fake on that will always be greater then itemduedate
                if itemenddate is None:
                    #Change to  = itemenddate + itemcycle (move below)
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
	        exitmsg.append(end_date)
                while itemduedate < end_date:
                    #Break loop, go to next item if due date is past budget end date
                    if itemduedate > itemenddate:
                        addedmsg.append("Out of Range: %s - %s" % (itemduedate, itemenddate))
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
                        exitstatus = 0
                        addedmsg.append('Added %s: %s - %s - %s' % (name,itemduedate,amount,paycycle))
                        itemduedate += itemcycle
                addedmsg.append("Out of Range: Due:%s - End:%s" % (itemduedate, end_date))
        #Exit with message
        return exitstatus, exitmsg, addedmsg
                    
				 
