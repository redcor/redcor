# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp import _, api, fields, models, tools
try:
    from openerp.addons.mail.models.mail_message import decode
    def decode_header(message, header, separator=' '):
        return separator.join(map(decode, filter(None, message.get_all(header, []))))
    
except ImportError:
    # odoo v 10
    from odoo.tools.mail import decode_message_header as decode_header

import logging
import time

_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 50

# set your domain
# (better to fetch it from email setttings)
DOMAIN = 'redcor.ch'

# use the following exception if you want to handle
# emails without model and parent_id differently
# for example to delete them
# class FetchallError(Exception):
#     def __init__(self, arg):
#         # Set some exception infomation
#         self.msg = arg




class MailThread(osv.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route_verify(self, message, message_dict, route, update_author=True, assert_model=True, create_fallback=True, allow_private=False):
        """ Verify route validity. Check and rules:
            1 - if thread_id -> check that document effectively exists; otherwise
                fallback on a message_new by resetting thread_id
            2 - check that message_update exists if thread_id is set; or at least
                that message_new exist
            [ - find author_id if udpate_author is set]
            3 - if there is an alias, check alias_contact:
                'followers' and thread_id:
                    check on target document that the author is in the followers
                'followers' and alias_parent_thread_id:
                    check on alias parent document that the author is in the
                    followers
                'partners': check that author_id id set
        """

        assert isinstance(route, (list, tuple)), 'A route should be a list or a tuple'
        assert len(route) == 5, 'A route should contain 5 elements: model, thread_id, custom_values, uid, alias record'

        message_id = message.get('Message-Id')
        email_from = decode_header(message, 'From')
        author_id = message_dict.get('author_id')
        model, thread_id, alias = route[0], route[1], route[4]
        record_set = None

        def _create_bounce_email():
            bounce_to = decode_header(message, 'Return-Path') or email_from
            bounce_mail_values = {
                'body_html': '<div><p>Hello,</p>'
                             '<p>The following email sent to %s cannot be accepted because this is '
                             'a private email address. Only allowed people can contact us at this address.</p></div>'
                             '<blockquote>%s</blockquote>' % (message.get('to'), message_dict.get('body')),
                'subject': 'Re: %s' % message.get('subject'),
                'email_to': bounce_to,
                'auto_delete': True,
            }
            bounce_from = self.env['ir.mail_server']._get_default_bounce_address()
            if bounce_from:
                bounce_mail_values['email_from'] = 'MAILER-DAEMON <%s>' % bounce_from
            self.env['mail.mail'].create(bounce_mail_values).send()

        def _warn(message):
            _logger.info('Routing mail with Message-Id %s: route %s: %s',
                         message_id, route, message)

        # Wrong model
        if model and model not in self.pool:
            if assert_model:
                assert model in self.pool, 'Routing: unknown target model %s' % model
            _warn('unknown target model %s' % model)
            return ()

        # Private message: should not contain any thread_id
        if not model and thread_id:
            if assert_model:
                if thread_id:
                    raise ValueError('Routing: posting a message without model should be with a null res_id (private message), received %s.' % thread_id)
            _warn('posting a message without model should be with a null res_id (private message), received %s resetting thread_id' % thread_id)
            thread_id = 0
        # Private message: should have a parent_id (only answers)
        # new
        # Private message without model and without parent_id:
        if not model and not message_dict.get('parent_id') and assert_model:
            spam_catchall_user_name = 'spam_catch_all'
            users_model = self.env['res.users']
            spam_catch_all_user = users_model.search([['name', '=', spam_catchall_user_name]])
            spam_catch_all_user_email = '%s@%s' % (spam_catchall_user_name, DOMAIN)
            if not spam_catch_all_user:
                spam_catch_all_user = users_model.create(
                    {
                    'name': spam_catchall_user_name,
                    'email': spam_catch_all_user_email,
                    'login': spam_catch_all_user_email,
                    }
                )
            message_dict['parent_id'] = spam_catch_all_user
            message_dict['subject'] = message_dict.get('subject', '') + ' (email to %s)' % message_dict['to']
            message_dict['to'] = spam_catch_all_user_email
            model = 'res.partner'
            message_dict['omit_new_record'] = True
            # raise FetchallError('Routing: posting a message without model should be with a parent_id (private mesage).')
        #
        if model and thread_id:
            record_set = self.env[model].browse(thread_id)
        elif model:
            record_set = self.env[model]

        # Existing Document: check if exists; if not, fallback on create if allowed
        if thread_id and not record_set.exists():
            if create_fallback:
                _warn('reply to missing document (%s,%s), fall back on new document creation' % (model, thread_id))
                thread_id = None
            elif assert_model:
                # TDE FIXME: change assert to some real error
                assert record_set.exists(), 'Routing: reply to missing document (%s,%s)' % (model, thread_id)
            else:
                _warn('reply to missing document (%s,%s), skipping' % (model, thread_id))
                return False

        # Existing Document: check model accepts the mailgateway
        if thread_id and model and not hasattr(record_set, 'message_update'):
            if create_fallback:
                _warn('model %s does not accept document update, fall back on document creation' % model)
                thread_id = None
            elif assert_model:
                assert hasattr(record_set, 'message_update'), 'Routing: model %s does not accept document update, crashing' % model
            else:
                _warn('model %s does not accept document update, skipping' % model)
                return False

        # New Document: check model accepts the mailgateway
        if not thread_id and model and not hasattr(record_set, 'message_new'):
            if assert_model:
                if not hasattr(record_set, 'message_new'):
                    raise ValueError(
                        'Model %s does not accept document creation, crashing' % model
                    )
            _warn('model %s does not accept document creation, skipping' % model)
            return False

        # Update message author if asked
        # We do it now because we need it for aliases (contact settings)
        if not author_id and update_author:
            author_ids = self.env['mail.thread']._find_partner_from_emails([email_from], res_model=model, res_id=thread_id)
            if author_ids:
                author_id = author_ids[0]
                message_dict['author_id'] = author_id

        # Alias: check alias_contact settings
        if alias and alias.alias_contact == 'followers' and (thread_id or alias.alias_parent_thread_id):
            if thread_id:
                obj = record_set[0]
            else:
                obj = self.env[alias.alias_parent_model_id.model].browse(alias.alias_parent_thread_id)
            accepted_partner_ids = list(
                set(partner.id for partner in obj.message_partner_ids) |
                set(partner.id for channel in obj.message_channel_ids for partner in channel.channel_partner_ids)
            )
            if not author_id or author_id not in accepted_partner_ids:
                _warn('alias %s restricted to internal followers, skipping' % alias.alias_name)
                _create_bounce_email()
                return False
        elif alias and alias.alias_contact == 'partners' and not author_id:
            _warn('alias %s does not accept unknown author, skipping' % alias.alias_name)
            _create_bounce_email()
            return False

        if not model and not thread_id and not alias and not allow_private:
            return ()

        return (model, thread_id, route[2], route[3], None if self._context.get('drop_alias', False) else route[4])

    @api.model
    def message_route_process(self, message, message_dict, routes):
        # postpone setting message_dict.partner_ids after message_post, to avoid double notifications
        partner_ids = message_dict.pop('partner_ids', [])
        thread_id = False
        for model, thread_id, custom_values, user_id, alias in routes or ():
            if model:
                Model = self.env[model]
                if not (thread_id and hasattr(Model, 'message_update') or hasattr(Model, 'message_new')):
                    raise ValueError(
                        "Undeliverable mail with Message-Id %s, model %s does not accept incoming emails" %
                        (message_dict['message_id'], model)
                    )

                # disabled subscriptions during message_new/update to avoid having the system user running the
                # email gateway become a follower of all inbound messages
                MessageModel = Model.sudo(user_id).with_context(mail_create_nosubscribe=True, mail_create_nolog=True)
                if thread_id and hasattr(MessageModel, 'message_update'):
                    MessageModel.browse(thread_id).message_update(message_dict)
                else:
                    # if a new thread is created, parent is irrelevant
                    message_dict.pop('parent_id', None)
                    if not message_dict.get('omit_new_record'):
                        thread_id = MessageModel.message_new(message_dict, custom_values)
            else:
                if thread_id:
                    raise ValueError("Posting a message without model should be with a null res_id, to create a private message.")
                Model = self.env['mail.thread']
            if not hasattr(Model, 'message_post'):
                Model = self.env['mail.thread'].with_context(thread_model=model)
            new_msg = Model.browse(thread_id).message_post(subtype='mail.mt_comment', **message_dict)

            if partner_ids:
                # postponed after message_post, because this is an external message and we don't want to create
                # duplicate emails due to notifications
                new_msg.write({'partner_ids': partner_ids})
        return thread_id


class fetchmail_server(osv.osv):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    def fetch_mail(self, cr, uid, ids, context=None):
        """WARNING: meant for cron usage only - will commit() after each email!"""
        context = dict(context or {})
        context['fetchmail_cron_running'] = True
        mail_thread = self.pool.get('mail.thread')
        action_pool = self.pool.get('ir.actions.server')
        for server in self.browse(cr, uid, ids, context=context):
            _logger.info('start checking for new emails on %s server %s', server.type, server.name)
            context.update({'fetchmail_server_id': server.id, 'server_type': server.type})
            count, failed = 0, 0
            imap_server = False
            pop_server = False
            if server.type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            res_id = mail_thread.message_process(cr, uid, server.object_id.model,
                                                                 data[0][1],
                                                                 save_original=server.original,
                                                                 strip_attachments=(not server.attach),
                                                                 context=context)
                        # except FetchallError:
                        #     pass
                        except Exception:
                            _logger.info('Failed to process mail from %s server %s.', server.type, server.name, exc_info=True)
                            failed += 1
                        if res_id and server.action_id:
                            action_pool.run(cr, uid, [server.action_id.id], {'active_id': res_id, 'active_ids': [res_id], 'active_model': context.get("thread_model", server.object_id.model)})
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.type, server.name, exc_info=True)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            elif server.type == 'pop':
                try:
                    while True:
                        pop_server = server.connect()
                        (numMsgs, totalSize) = pop_server.stat()
                        pop_server.list()
                        for num in range(1, min(MAX_POP_MESSAGES, numMsgs) + 1):
                            (header, msges, octets) = pop_server.retr(num)
                            msg = '\n'.join(msges)
                            res_id = None
                            try:
                                res_id = mail_thread.message_process(cr, uid, server.object_id.model,
                                                                     msg,
                                                                     save_original=server.original,
                                                                     strip_attachments=(not server.attach),
                                                                     context=context)
                                pop_server.dele(num)
                            # except FetchallError:
                            #     pass
                                # pop_server.dele(num)
                            except Exception:
                                _logger.info('Failed to process mail from %s server %s.', server.type, server.name, exc_info=True)
                                failed += 1
                            if res_id and server.action_id:
                                action_pool.run(cr, uid, [server.action_id.id], {'active_id': res_id, 'active_ids': [res_id], 'active_model': context.get("thread_model", server.object_id.model)})
                            cr.commit()
                        if numMsgs < MAX_POP_MESSAGES:
                            break
                        pop_server.quit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", numMsgs, server.type, server.name, (numMsgs - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.type, server.name, exc_info=True)
                finally:
                    if pop_server:
                        pop_server.quit()
            server.write({'date': time.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)})
        return True
