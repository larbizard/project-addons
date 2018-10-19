# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.thread']

    code = fields.Char(
        string='Number',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Responsible',
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )
    project_type = fields.Selection(
        [
            ('event', 'Event'),
            ('project', 'Project'),
        ],
        string='Type',
        default='project',
    )
    notes = fields.Html(string='Notes')
    description = fields.Html(string='Description')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('option', 'Option'),
            ('accepted', 'Accepted'),
            ('postponed', 'Postponed'),
            ('canceled', 'Canceled')
        ],
        string='State',
        default='draft',
        track_visibility='onchange',
    )
    event_log_count = fields.Integer(
        string='Event Logs',
        compute='_compute_event_log_count',
    )

    def _compute_event_log_count(self):
        for rec in self:
            rec.event_log_count = self.env['auditlog.log'].search_count([
                ('model_id', '=', self.env.ref(
                    'project.model_project_project').id),
                ('res_id', '=', rec.id)
            ])

    @api.multi
    def action_cancel(self):
        self.write({'state': 'canceled'})

    @api.multi
    def action_accept(self):
        self.write({'state': 'accepted'})

    @api.multi
    def action_option(self):
        self.write({'state': 'option'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        if 'project_type' in vals:
            if vals['project_type'] == 'event':
                vals['code'] = self.env['ir.sequence'] \
                    .next_by_code('project.project')
        return super(Project, self).create(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name),
                      ('code', operator, name)]
        return super(Project, self).search(
            domain + args, limit=limit).name_get()

    def get_message_body(self, action):
        switcher = {
            'draft': ' ',
            'option': _('The following are Optional\
                        and appear and are hatched on the calendar'),
            'accepted': ' ',
            'postponed': _('The following are postponed \
                        and no longer appear on your calendars'),
            'canceled': _('The following is canceled\
                         and no longer on your calendars')
        }
        return switcher.get(action)

    def get_message(self, action):
        return {
            'body': self.get_message_body(action),
            'channel_ids': [(6, 0, [self.env.ref
                            ('project.mail_channel_project_task').id])],
            'email_from': 'Administrator <admin@yourcompany.example.com>',
            'message_type': 'notification',
            'model': 'project.task',
            'partner_ids': [(6, 0, [self.task_responsible_id.id])],
            'record_name': self.name,
            'reply_to': 'Administrator <admin@yourcompany.example.com>',
            'res_id': self.id,
            'subject': self.code
        }

    def send_message(self, action):
        self.env['mail.message'].create(self.get_message(action))
