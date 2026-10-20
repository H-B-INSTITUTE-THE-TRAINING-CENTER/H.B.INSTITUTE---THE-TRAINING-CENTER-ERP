from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Examination(models.Model):
    _name = "examination"
    _description = "Student Examination"
    _order = "exam_date desc, name"

    name = fields.Char(
        string="Examination Name",
        required=True
    )

    course_id = fields.Many2one(
        "course",
        string="Course",
        required=True, 
        ondelete='restrict'
    )

    batch_id = fields.Many2one(
        "batch",
        string="Batch", 
        required=True, 
        ondelete='restrict'
    )

    exam_date = fields.Date(
        string="Examination Date",
        required=True
    )

    start_time = fields.Float(
        string = "Start Time"
    )

    duration_minutes = fields.Integer(
        string="Duration (Minutes)",
        default=60,
        required=True
    )

    exam_type = fields.Selection(
        [
            ("practical","Practical"),
            ("project","Project")
        ],

        string="Examination Type",
        default="practical",
        required=True
    )

    status = fields.Selection(
        [
            ("draft","Draft"),
            ("scheduled","Scheduled"),
            ("completed","Completed"),
            ("cancelled","Cancelled")
        ],
        string = "Status",
        default = "draft",
        required = True
    )

    notes = fields.Text(
        string = "Notes"
    )

    active = fields.Boolean(
        string = "Active",
        default = True
    )


    @api.constrains("course_id","batch_id")
    def _check_course_batch(self):
        for record in self:
            if record.course_id and record.batch_id and record.batch_id.course_id != record.course_id:
                raise ValidationError("The selected batch must belong to selected course.")

    @api.constrains("duration_minutes")
    def _check_duration(self):
        for record in self:
            if record.duration_minutes <= 0:
                raise ValidationError("Examination duration must be greater than zero.")

    def action_schedule(self):
        for record in self:
            if record.status != "draft":
                raise ValidationError("Only draft examinations can be scheduled.")
            record.status = "scheduled"

    def action_complete(self):
        for record in self:
            if record.status != "scheduled":
                raise ValidationError("Only scheduled examinations can be completed.")
            record.status = "completed"

    def action_cancel(self):
        for record in self:
            if record.status not in ("draft","scheduled"):
                raise ValidationError("Only draft or scheduled examinations can be cancelled.")
            record.status = "cancelled"