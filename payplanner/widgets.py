#widgets.py
#Author: Matt Agresta
#Created On: 10/10/2016
#Custom payplanner widgets
import copy
import re

from calendar import HTMLCalendar
from datetime import date

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.forms import widgets
from django.conf import settings

from payplanner.budget import Budget

from bs4 import BeautifulSoup

class BillendarHTML(HTMLCalendar):

    """Class to form html calendar html widgets with budget info"""

    def __init__(self, firstweekday, user):

        super(BillendarHTML, self).__init__(firstweekday)

        self.user = user

    def formatmonth(self, theyear, themonth):

        output = []
        calendaritems = {}
        #template for budget elements
        html_doc = "<div></div>"
        element = BeautifulSoup(html_doc, 'html.parser')
        #Get Budget for self.user for month
        lineitems = Budget.build(self.user,month=(themonth,theyear))
        for line in lineitems:
            
            #Create html div element for each budget line
            line_ele = copy.copy(element)
            tag = line_ele.div
            display = ("%s - %s" % (line['name'],line['amount']))
            tag.string = display
            tag['id'] = line['itemid']
            tag['data-note'] = line['itemnote']
            tag['data-cycle'] = line['cycle']
            tag['class'] = "modal-form-trigger"
            itemdate = line['itemdate']
            #Create children elements
            children = {'id_effectiveDate': line['itemdate'],
                        'id_itemName': line['name'],
                        'id_parentItem': line['parent'],
                        'id_itemAmmount': line['amount'],
                        'id_runningTotal': line['running_total']}
            #css properties
            nodisplay = "display:none;"
            for key,val in children.iteritems():
                
                child = element.new_tag("div")
                child['name'] = key
                child['style'] = nodisplay
                child.string = str(val)
                tag.append(child)

            try:
                calendaritems[itemdate].append(line_ele)
            except KeyError:
                calendaritems[itemdate] = [line_ele,]
                
            
                                    
        #Render Initial HTML
        html_doc = super(BillendarHTML, self).formatmonth(theyear, themonth)

        #Parse calendar and add in budget items
        soup = BeautifulSoup(html_doc, 'html.parser')
        table = soup.table

        for daycell in table.find_all("td"):
            testvar = daycell.text
            if daycell['class'] == 'noday':
                continue
            theday = daycell.string
            curdate = date(theyear, themonth, theday)
            #Insert any items matching curdate
            #for ele in calendaritems[curdate]:
                #daycell.append(ele)
        #output.append(table)    
        return curdate
        #return mark_safe(u''.join(output))
        
class RelatedFieldWidgetAddEdit(widgets.Select):

    def __init__(self, related_model, view_name, add_url=None, edit_url=None, to_page=None, *args, **kw):

        super(RelatedFieldWidgetAddEdit, self).__init__(*args, **kw)

        # Be careful that here "reverse" is not allowed
        self.add_url = add_url
        self.edit_url = edit_url
        self.to_page = to_page
        self.view_name = view_name

    def render(self, name, value, *args, **kwargs):
        #self.add_url = reverse(self.related_url)
        output = []
        #Add Link
        if self.add_url:
            alt = 'Add Another'
            output.append(u'<a href="%s" class="add-another right" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
                (self.add_url, name))
            output.append(u'<img src="%sadmin/img/icon_addlink.gif" width="10" height="10" alt="%s"/></a>&nbsp&nbsp' % (settings.STATIC_URL, alt))

        #Edit Button
        if self.edit_url:
            alt = 'Edit List'
            output.append(u'<button type="submit" name="%s_btn" value="edit_%s" class="btn-edit-rel">' % (self.view_name, name))
            output.append(u'<i class="material-icons form-widget">mode_edit</i></button>')
            
        selectobj = super(RelatedFieldWidgetAddEdit, self).render(name, value, *args, **kwargs)
        output.append(selectobj)
        
        return mark_safe(u''.join(output))
