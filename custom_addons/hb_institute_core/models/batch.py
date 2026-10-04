from odoo import models, fields

class Batch(models.Model):
    _name = "batch"
    _description = "Training Batch"
    _order = "start_date desc"

    name = fields.Char(
        string = "Batch Name",
        required = True
    )

    course_id = fields.Many2one(
        "course",
        string = "Course",
        required = True,
        ondelete = "restrict"
    )

    faculty = fields.Char(
        string = "Faculty"
    )

    start_date = fields.Date(
        string = "Start Date"
    )

    end_date = fields.Date(
        string = "End Date"
    )

    start_time = fields.Float(
        string = "Start Time"
    )

    end_time = fields.Float(
        string = "End Time"
    )

    capacity = fields.Integer(
        string = "Capacity",
        default = 5
    )

    status = fields.Selection(
        [
            ("planned","Planned"),
            ("running","Running"),
            ("completed","Completed"),
            ("cancelled","Cancelled")
        ],
        string = "Status",
        default = "planned",
        required = True
    )

    active = fields.Boolean(
        string = "Active",
        default = True
    )

    notes = fields.Text(
        string = "Notes"
    )

    student_ids = fields.One2many(
        "student",
        "batch_id",
        string = "Students"
    )

    enrollment_ids = fields.One2many(
        "enrollment",
        "batch_id",
        string = "Enrollments"
    )
