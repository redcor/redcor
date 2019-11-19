# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp import SUPERUSER_ID
import logging
#Get the logger
_logger = logging.getLogger(__name__)

class WebsiteCmsMenu(models.Model):
    _name = 'website.cms_menu'
    _inherit = 'res.config.settings'

    main_frame = fields.Many2one("cms.page", string="Main Menu Root")
    front_cms = fields.Many2one("cms.page", string="Front Cms Page")
    template_menu_id = fields.Boolean(default=False, string="Home Menu",)
    template_imagegrid_id = fields.Boolean(default=False, string="Image Grid",)

    def get_default_main_frame(self, cr, uid, ids, context=None):
        """
        Getting default config values
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """
        ir_values = self.pool.get('ir.values')

        main_frame = ir_values.get_default(cr, uid, 'website.cms_menu', 'main_frame')
        front_cms = ir_values.get_default(cr, uid, 'website.cms_menu', 'front_cms')
        template_menu_id = ir_values.get_default(cr, uid, 'website.cms_menu', 'template_menu_id')
        template_imagegrid_id = ir_values.get_default(cr, uid, 'website.cms_menu', 'template_imagegrid_id')
        return {
            'main_frame': main_frame,
            'front_cms': front_cms,
            'template_menu_id': template_menu_id,
            'template_imagegrid_id': template_imagegrid_id,
        }

    def set_default_main_frame(self, cr, uid, ids, context=None):
        """
        setting default values
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """
        ir_values = self.pool.get('ir.values')

        wizard = self.browse(cr, uid, ids)[0]
        if wizard.main_frame:
            main_frame = wizard.main_frame
            front_cms = wizard.front_cms
            template_menu_id = wizard.template_menu_id
            template_imagegrid_id = wizard.template_imagegrid_id
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'template_menu_id', template_menu_id)
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'template_imagegrid_id', template_imagegrid_id)
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'main_frame', main_frame.id)
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'front_cms', front_cms.id)
        else:
            main_frame = False
            front_cms = False
            template_menu_id = False
            template_imagegrid_id = False
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'template_menu_id', template_menu_id)
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'template_imagegrid_id', template_imagegrid_id)
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'main_frame', main_frame)
            ir_values.set_default(cr, SUPERUSER_ID, 'website.cms_menu', 'front_cms', front_cms)


class event_config_settings(models.Model):

    _name = 'event.settings'
    _inherit = 'res.config.settings'
    
    root_cms_page_id = fields.Many2one('cms.page', "Root CMS Page")

    def get_default_root_cms_page_id(self, cr, uid, ids, context=None):
        """
        Getting default config values
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """
        ir_values = self.pool.get('ir.values')
        root_cms_page_id = ir_values.get_default(cr, uid, 'event.settings', 'root_cms_page_id')
        return {
            'root_cms_page_id': root_cms_page_id,
        }
    
    def set_default_root_cms_page_id(self, cr, uid, ids, context=None):
        """
        setting default values
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """
        ir_values = self.pool.get('ir.values')
        wizard = self.browse(cr, uid, ids)[0]
        if wizard.root_cms_page_id:
            root_cms_page_id = wizard.root_cms_page_id
            ir_values.set_default(cr, SUPERUSER_ID, 'event.settings', 'root_cms_page_id', root_cms_page_id.id)
        else:
            root_cms_page_id = False
            ir_values.set_default(cr, SUPERUSER_ID, 'event.settings', 'root_cms_page_id', root_cms_page_id)
            
            
class EventCms(models.Model):
    _name = 'cms.page'
    _inherit = ["cms.page"]
    
    # copied from afbs_cms/wizard/cms_page_unlink_hierarchy.py
    def unlink_children(self, clist):
        cms_object = self.env['cms.page']
        for c in clist:
            children = cms_object.search([('parent_id', '=', c.id)])
            if len(children):
                self.unlink_children(children)
            media = self.env['cms.media'].search([('res_id', 'in', c.ids)])
            if media:
                for cms_media in media:
                    cms_media.unlink()
            c.unlink()
                           
    @api.model
    def clean_orphans(self):
        event_settings = self.env['event.settings']
        root_cms_page_id = event_settings.get_default_root_cms_page_id()['root_cms_page_id']
        # with root_cms_page_id we can collect all cms pages that are direct children of the events root page
        cms_pages = self.env['cms.page']
        # event_root_page = cms_pages.browse(root_cms_page_id)
        event_pages = cms_pages.search([('parent_id', '=', root_cms_page_id)])
        event_page_ids = [e.id for e in event_pages]
        # next we collect all events and remove their cmspage id's from event_page_ids
        event_model = self.env['event.event']
        # execute a query directly
        self.env.cr.execute('select cms_page_id from event_event')
        result = self.env.cr.dictfetchall()
        for e in result:
            try:
                i = event_page_ids.index(e['cms_page_id'])
                event_page_ids.pop(i)
            except Exception as e:
                # should not happen
                a=1
        # what remains in event_page_ids, are orphanded cms pages
        if event_page_ids:
            for cms_page in cms_pages.browse(event_page_ids):
                children = cms_page.children_ids
                self.unlink_children(children)
                media = self.env['cms.media'].search([('res_id', 'in', cms_page.ids)])
                if media:
                    for cms_media in media:
                        cms_media.unlink()
                cms_page.unlink()
                
        _logger.info('deleted %s orphaned event cms pages' % len(event_page_ids))         