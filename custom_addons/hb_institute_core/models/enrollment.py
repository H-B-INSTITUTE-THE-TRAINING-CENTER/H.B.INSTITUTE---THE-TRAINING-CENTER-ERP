from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Enrollment(models.Model):
    _name = "enrollment"
    _description = "Student Enrollment"
    _order = "admission_date desc, id desc"
    _rec_name = "admission_number"
    _sql_constraints = [
        (
            "unique_admission_number",
            "unique(admission_number)",
            "Admission Number must be unique."
        )
    ]

    admission_number = fields.Char(
        string = "Admission Number",
        required = True,
        copy = False,
        readonly = True,
        default = "New",
        index = True
    )

    admission_date = fields.Date(
        string = "Admission Date",
        required = True,
        default = fields.Date.today
    )

    student_id = fields.Many2one(
        "student",
        string = "Student",
        required = True,
        ondelte = "restrict"
    )

    course_id = fields.Many2one(
        "course",
        string = "Course",
        required = True,
        ondelete = "restrict"
    )

    batch_id = fields.Many2one(
        "batch",
        string = "Batch",
        required = True,
        ondelete = "restrict",
        domain = "[('course_id','=',course_id)]"
    )

    course_fee = fields.Float(
        string = "Course Fee",
        related = "course_id.fees",
        store = True,
        readonly = True
    )

    discount = fields.Float(
        string = "Discount",
        default = 0.0
    )

    final_fee = fields.Float(
        string = "Final Fee",
        compute = "_compute_final_fee",
        store = True
    )

    status = fields.Selection(
        selection = [
            ("draft","Draft"),
            ("confirmed","Confirmed"),
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

    @api.depends("course_fee","discount")
    def _compute_final_fee(self):
        for record in self:
            record.final_fee = record.course_fee - record.discount

    @api.constrains("course_id","batch_id")
    def _check_batch_course(self):
        for record in self:
            if record.course_id and record.batch_id and record.batch_id.course_id != record.course_id:
                raise ValidationError(
                    "The selected batch does not belong to the selected course"
                )

    @api.constrains("discount","course_fee")
    def _check_discount(self):
        for record in self:
            if record.discount < 0:
                raise ValidationError(
                    "Discount cannot be negative."
                )
            if record.discount > record.course_fee:
                raise ValidationError(
                    "Discount cannot be greater than the course fee."
                )

    @api.constrains("final_fee")
    def _check_final_fee(self):
        for record in self:
            if record.final_fee < 0:
                raise ValidationError(
                    "Final Fee cannot be negative."
                )

    @api.constrains("batch_id")
    def _check_batch_status(self):
        for record in self:
            if record.batch_id:
                if record.batch_id.status in ("completed","cancelled"):
                    raise ValidationError(
                        "You cannot enroll a student into a completed or cancelled batch."
                    )

    @api.constrains("batch_id")
    def _check_batch_active(self):
        for record in self:
            if record.batch_id and not record.batch_id.active:
                raise ValidationError(
                    "You cannot enroll a student into an inactive batch."
                )

    @api.constrains("batch_id","status")
    def _check_batch_capacity(self):
        for record in self:
            if not record.batch_id:
                continue
            if record.status not in ("confirmed","completed"):
                continue
            confirmed_enrollments = self.search_count([
                ("batch_id","=",record.batch_id.id),
                ("status","in",["confirmed","completed"]),
                ("id","!=",record.id)
            ])

            if confirmed_enrollments >= record.batch_id.capacity:
                raise ValidationError(
                    "This batch has reached its maximum capacity."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("admission_number", "New") == "New":
                vals["admission_number"] = self.env["ir.sequence"].next_by_code("enrollment.sequence") or "New"
        return super().create(vals_list)

    def action_confirm(self):
        for record in self:
            record.status = "confirmed"
            record.student_id.write({
                "status":"active",
                "course_id":record.course_id.id,
                "batch_id":record.batch_id.id
            })

    def action_complete(self):
        for record in self:
            record.status = "completed"
            record.student_id.write({
                "status":"completed"
            })

    def action_cancel(self):
        for record in self:
            record.status = "cancelled"

    def action_reset_to_draft(self):
        for record in self:
            record.status = "draft"