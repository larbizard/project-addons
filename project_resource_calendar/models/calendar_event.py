# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    resource_type = fields.Selection([
        ('user', 'Human'),
        ('equipment', 'Equipment'),
        ('room', 'Room')], string='Resource Type',
        default='room', required=True)

    room_ids = fields.Many2many(
        string='Room',
        comodel_name='resource.calendar.room',
        ondelete='set null',
    )
    equipment_ids = fields.Many2many(
        string='Equipment',
        comodel_name='resource.calendar.instrument',
        ondelete='set null',
    )
