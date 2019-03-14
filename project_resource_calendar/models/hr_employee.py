# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    allow_double_book = fields.Boolean(
        string='Allow Double Booking',
        help='Check if this employee '
             'can be booked as a participant in more than '
             'one meeting or event at the same '
             'time.',
        readonly=True,
        related='user_id.partner_id.allow_double_book',
    )