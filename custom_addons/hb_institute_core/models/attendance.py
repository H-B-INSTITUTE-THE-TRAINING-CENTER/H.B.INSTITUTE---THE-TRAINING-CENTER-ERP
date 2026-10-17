from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Attendance(models.Model):
    _name = "attendance"
    _description = "Student Attendance"
    _rec_name = "student_id"
    _order = "attendance_date desc, id desc"

    student_id = fields.Many2one(
        "student",
        string="Student",
        required=True,
        ondelete="restrict",
        index=True,
    )

    batch_id = fields.Many2one(
        "batch",
        string="Batch",
        required=True,
        ondelete="restrict",
        index=True,
    )

    attendance_date = fields.Date(
        string="Attendance Date",
        required=True,
        default=fields.Date.context_today,
        index=True,
    )

    status = fields.Selection(
        [
            ("present", "Present"),
            ("absent", "Absent"),
            ("late", "Late"),
            ("cancelled", "Cancelled"),
        ],
        string="Attendance Status",
        required=True,
        default="present",
    )

    remarks = fields.Text(string="Remarks")
    _sql_constraints = [
            (
                "unique_student_batch_date",
                "unique(student_id, batch_id, attendance_date)",
                "Attendance for this student, batch, and date already exists.",
            ),
        ]
    

    @api.onchange("student_id")
    def _onchange_student_id(self):
        for record in self:
            if record.student_id:
                if record.student_id.batch_id:
                    record.batch_id = record.student_id.batch_id
                    return {
                        "domain": {
                            "batch_id": [
                                ("id", "=", record.student_id.batch_id.id)
                            ]
                        }
                    }
                else:
                    record.batch_id = False
                    return {
                        "warning": {
                            "title": "Batch Not Assigned",
                            "message": (
                                "This student has no assigned batch. "
                                "Assign a batch to the student before "
                                "recording attendance."
                            ),
                        }
                    }

    @api.constrains("student_id", "batch_id")
    def _check_student_batch(self):
        for record in self:
            if not record.student_id or not record.batch_id:
                continue

            if not record.student_id.batch_id:
                raise ValidationError(
                    "The selected student has no assigned batch. "
                    "Assign a batch to the student first."
                )

            if record.student_id.batch_id != record.batch_id:
                raise ValidationError(
                    "The selected batch does not match the student's "
                    "currently assigned batch."
                )

    @api.constrains("attendance_date")
    def _check_attendance_date(self):
        for record in self:
            if not record.attendance_date:
                raise ValidationError(
                    "Attendance date is required."
                )

            if record.attendance_date > fields.Date.context_today(record):
                raise ValidationError(
                    "Attendance date cannot be in the future."
                )

    @api.constrains("student_id","batch_id","attendance_date")
    def _check_duplicate_attendance(self):
        for record in self:
            if not (record.student_id and record.batch_id and record.attendance_date):
                continue
            duplicate = self.search_count([
                ("student_id","=",record.student_id),
                ("batch_id","=",record.batch_id.id),
                ("attendance_date","=",record.attendance_date),
                ("id","!=",record.id)
            ])

            if duplicate:
                raise ValidationError("Attendance already exists for this student, batch and date")