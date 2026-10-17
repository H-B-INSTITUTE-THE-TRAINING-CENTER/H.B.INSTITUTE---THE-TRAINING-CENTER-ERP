from odoo import models, fields, api

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
        ], # type: ignore
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

    enrolled_count = fields.Integer(
        string = "Enrolled Students",
        compute = "_compute_enrollment_stats",
        store = True
    )

    available_seats = fields.Integer(
        string="Available Seats",
        compute = "_compute_enrollment_stats",
        store = True
    )

    @api.depends("capacity","enrollment_ids.status")
    def _compute_enrollment_stats(self):
        for record in self:
            enrolled = len(
                record.enrollment_ids.filtered(
                    lambda enrollment: enrollment.status in ("confirmed","completed") # type: ignore
                )
            )
            record.enrolled_count = enrolled
            record.available_seats = max(record.capacity - enrolled, 0)
