#widgets.py
#Author: Matt Agresta
#Created On: 10/10/2016
#Custom payplanner widgets

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.forms import widgets
from django.conf import settings

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
