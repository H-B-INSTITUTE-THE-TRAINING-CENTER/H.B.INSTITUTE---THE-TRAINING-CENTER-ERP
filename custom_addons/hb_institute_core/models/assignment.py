from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Assignment(models.Model):
    _name = "assignment"
    _description = "Student Assignment"
    _order = "deadline desc, name"

    name = fields.Char(
        string = "Assignment Title",
        required = True
    )

    description = fields.Html(
        string = "Instructions",
        required = True
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
        ondelete = "restrict"
    )

    assigned_date = fields.Date(
        string = "Assigned Date",
        default = fields.Date.today,
        required = True
    )

    deadline = fields.Date(
        string = "Submission Deadline",
        required = True
    )

    submission_ids = fields.One2many(
        "assignment.submission",
        "assignment_id",
        string = "Student Submissions"

    )

    pending_count = fields.Integer(
        string="Pending",
        compute="_compute_reporting_stats"
    )

    submitted_count = fields.Integer(
        string="Submitted",
        compute="_compute_reporting_stats"
    )

    evaluated_count = fields.Integer(
        string="Evaluated",
        compute="_compute_reporting_stats"
    )

    overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_reporting_stats",
        search="_search_overdue"
    )

    notes = fields.Text(string = "Internal Notes")

    active = fields.Boolean(
        string = "Active",
        default = True
    )

    @api.depends("deadline", "submission_ids.status")
    def _compute_reporting_stats(self):
        today = fields.Date.context_today(self)

        for record in self:
            submissions = record.submission_ids

            pending = submissions.filtered(
                lambda sub: sub.status == "pending"
            )

            submitted = submissions.filtered(
                lambda sub: sub.status in ("submitted", "late")
            )

            evaluated = submissions.filtered(
                lambda sub: sub.status == "evaluated"
            )

            record.pending_count = len(pending)
            record.submitted_count = len(submitted)
            record.evaluated_count = len(evaluated)

            record.overdue = bool(
                record.deadline
                and record.deadline < today
                and pending
            )

    @api.constrains("assigned_date","deadline")
    def _check_assignment_dates(self):
        for record in self:
            if(record.assigned_date and record.deadline and record.deadline < record.assigned_date):
                raise ValidationError("The submission deadline cannot be before the assigned date.")

    @api.constrains("course_id","batch_id")
    def _check_course_batch(self):
        for record in self:
            if(record.course_id and record.batch_id and record.batch_id.course_id != record.course_id):
                raise ValidationError("The selected batch must belong to the selected course.")

    @api.model
    def _search_overdue(self, operator, value):
        today = fields.Date.context_today(self)

        overdue_domain = [
            "&",
            ("deadline", "<", today),
            ("submission_ids.status", "=", "pending"),
        ]

        if operator not in ("=", "!="):
            return []

        want_overdue = bool(value)

        if operator == "!=":
            want_overdue = not want_overdue

        if want_overdue:
            return overdue_domain

        return ["!"] + overdue_domain