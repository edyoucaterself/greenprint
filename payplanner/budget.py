from .models import Items, BudgetData, Cycles
from dateutil.relativedelta import relativedelta
from datetime import date
import json
#TODO
#Build - Check if item exists already in budget, if not add it
#Update Budget - Called on item alter - Remove item, run build again
#If item altered -
#   Ammount Changed - alter entries with date > today
#   End Date specified - Remove any entries with date > new enddate
#   End Date changed
#       newdate < original date - See End Date Specified (above)
#       newdate > original date - Run build method
#Class usage:
#instance = Budget(expense/income query object, form.has_changed() object)
class Budget():
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
    def build(username):
        #Grab all items from BudgetData and sort by date and then income/expense
        itemlst = BudgetData.objects.values().filter(parentItem__user=username).order_by('effectiveDate','-parentItem__itemType')
        running_total = 0
        budget_output = []
        linenum = 1
        for line in itemlst:
            item = BudgetData.objects.get(pk=line['id'])
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
    #Add optional passable variable to store newly added item
    #   If item is passed do 'items = Items.objects.values().filter(itemName=passed_data), else - what we have now
    @staticmethod
    def update_data(optdict):
	today = date.today()
	yearlen = relativedelta(months=optdict['months'])
	username=optdict['user']
	end_date = today + yearlen
	#Clean up anything past the end_date
	BudgetData.objects.filter(effectiveDate__gt=end_date).filter(parentItem__user=username).delete()
	#Get Items to build BudgetData
	items = Items.objects.values().filter(user=username)
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
                else:
                    itemcycle = relativedelta(days=cyclength)
	
                while itemduedate < end_date:
                    #Issue with running this second time on single EMS item, posssible others

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
                        data = BudgetData(parentItem = item, effectiveDate = itemduedate,itemAmmount = amount)
                        data.save()
                        print('Added %s: %s - %s - %s' % (name,itemduedate,amount,paycycle))
                        itemduedate += itemcycle
                    
                #Clean up anything older than beginning time frame
                    
				 
