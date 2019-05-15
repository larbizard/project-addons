# Copyright 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class RoomType(models.Model):
    _name = 'resource.calendar.room.type'
    _order = 'sequence, name'

    name = fields.Char(
        string='Room Type'
    )
    sequence = fields.Integer(
        string='Sequence',
    )
