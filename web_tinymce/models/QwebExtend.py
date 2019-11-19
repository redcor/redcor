# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.base.ir.ir_qweb import QWeb

class QWebExtend(QWeb):
    
    def render_tag_call_assets(self, element, template_attributes, generated_attributes, qwebcontext):
        # do notcheck whether we want to return minified assets
        cr = qwebcontext.get('request') and qwebcontext['request'].cr or None
        uid = qwebcontext.get('request') and qwebcontext['request'].uid or None
        do_not_minify = self.user_has_groups(cr, uid, groups='base.group_user') if cr and uid else False
        if do_not_minify:
            # do not returned minified assets
            # by pretending that the dbug mode is active
            qwebcontext['debug'] = True
        return super(QWebExtend, self).render_tag_call_assets(element, template_attributes, generated_attributes, qwebcontext)
        