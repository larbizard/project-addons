# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.thread']

    code = fields.Char(
        string='Number',
        track_visibility='onchange',
    )
    responsible_id = fields.Many2one(
        'res.partner',
        string='Event Responsible',
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        track_visibility='onchange',
    )
    client_type = fields.Many2one(
        'res.partner.category.type',
        string='Client Type',
        track_visibility='onchange',
    )
    sector_id = fields.Many2one(
        'res.partner.sector',
        string='Faculty Sector',
        track_visibility='onchange',
    )
    project_type = fields.Selection(
        [
            ('event', 'Event'),
            ('project', 'Project'),
        ],
        string='Type',
        default='project',
    )
    description = fields.Html(
        string='Description'
    )
    notes = fields.Html(
        string='Notes',
        track_visibility='onchange',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('option', 'Option'),
            ('approved', 'Approved'),
            ('postponed', 'Postponed'),
            ('canceled', 'Canceled')
        ],
        string='State',
        default='draft',
        track_visibility='onchange',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.client_type = self.partner_id.tag_id.client_type

    @api.multi
    def write(self, vals):
        super(Project, self).write(vals)
        if self.project_type == 'event':
            self.write_activity(vals)

    @api.multi
    def write_activity(self, vals):
        activity_vals = {}
        if 'responsible_id' in vals:
            activity_vals['responsible_id'] = vals['responsible_id']
        if 'partner_id' in vals:
            activity_vals['partner_id'] = vals['partner_id']
        if 'client_type' in vals:
            activity_vals['client_type'] = vals['client_type']
        if 'sector_id' in vals:
            activity_vals['sector_id'] = vals['sector_id']
        for activity in self.task_ids:
            if activity_vals:
                activity.write(activity_vals)

    @api.multi
    def action_cancel(self):
        if self.state == 'approved':
            pass
        for activity in self.task_ids:
            activity.action_cancel()
        self.write({'state': 'canceled'})

    @api.multi
    def action_accept(self):
        #validation wizard
        pass 

    @api.multi
    def action_option(self):
        #validation wizard
        pass

    @api.multi
    def action_postpone(self):
        if self.state == 'approved':
            pass
        for activity in self.task_ids:
            activity.action_postpone()
        self.write({'state': 'postponed'})

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

    @api.multi
    def confirm_accept_reservation(self):
        for activity in self.task_ids:
            if activity.task_state in [
                    'draft', 'option', 'postponed', 'canceled']:
                for child in activity.child_ids:
                    self.child_reservation(child)
                pass
            activity.open_resources_reservation()
            activity.write({'task_state': 'approved'})
        if self.state in ['draft', 'option', 'postponed', 'canceled']:
            pass
        self.write({'state': 'approved'})

    @staticmethod
    def child_reservation(child):
        child.draft_resources_reservation()
        if child.task_state in ['draft', 'option', 'postponed',
                                'canceled']:
            pass
        child.open_resources_reservation()
        child.write({'task_state': 'requested'})

    @api.multi
    def map_tasks(self, new_project_id):
        """ copy and map tasks from old to new project """
        tasks = self.env['project.task']
        task_ids = self.env['project.task'].with_context(
            active_test=False).search([('project_id', '=', self.id)]).ids
        for task in self.env['project.task'].browse(task_ids):
            defaults = {
                'stage_id': task.stage_id.id,
                'name': _("%s (copy)") % task.name,
                'project_id': new_project_id}
            tasks += task.copy(defaults)
        return self.browse(new_project_id)


    @staticmethod
    def order_event_fields(tracking_values):
        event_fields_list = [
            'state',
            'name',
            'code',
            'responsible_id',
            'partner_id',
            'notes',
            'user_id'
        ]
        event_tracking_values = []
        for index in range(len(tracking_values)):
            for k in range(len(event_fields_list)):
                event = tracking_values.__getitem__(index)
                if event.__getitem__(2).get('field') \
                        == event_fields_list[k]:
                    event_tracking_values.append(event)
        return event_tracking_values
