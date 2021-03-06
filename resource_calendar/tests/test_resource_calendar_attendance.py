# Copyright 2017 Laslabs Inc.
# Copyright 2018 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import ValidationError
from .setup import Setup


class TestResourceCalendarAttendance(Setup):

    def setUp(self):
        super(TestResourceCalendarAttendance, self).setUp()
        self.attendance_1 = self.env['resource.calendar.attendance'].create({
            'name': 'Monday morning',
            'dayofweek': 0,
            'hour_from': 8,
            'hour_to': 12,
            'calendar_id': self.calendar_40_h.id
        })

    def test_check_date_from_date_to(self):
        """ Test raise ValidationError if dates not in order """
        with self.assertRaises(ValidationError):
            self.attendance_1.write({
                'date_from': fields.Date.from_string('2016-06-06'),
                'date_to': fields.Date.from_string('2016-05-05'),
            })

    def test_check_hour_from_hour_to(self):
        """ Test raise ValidationError if hours not in order """
        with self.assertRaises(ValidationError):
            self.attendance_1.write({
                'hour_from': 5.00,
                'hour_to': 4.00,
            })
