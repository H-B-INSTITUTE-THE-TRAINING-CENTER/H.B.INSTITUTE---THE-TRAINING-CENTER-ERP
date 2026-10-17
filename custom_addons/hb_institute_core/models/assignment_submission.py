from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AssignmentSubmission(models.Model):
    _name = "assignment.submission"
    _description = "Assignment Submission"
    _order = "submitted_date desc, id desc"

    _student_assignment_unique = models.Constraint(
        "UNIQUE(assignment_id, student_id)",
        "A student can have only one submission record per assignment"
    )

    assignment_id = fields.Many2one(
        "assignment",
        string = "Assignemnt",
        required = True,
        ondelete='cascade'
    )

    student_id = fields.Many2one(
        "student",
        string = "Student",
        required=True,
        ondelete='restrict'
    )

    batch_id = fields.Many2one(
        "batch",
        string="Batch",    
        related='assignment_id.batch_id',
        readonly=True,
        store=True
    )

    course_id = fields.Many2one(
        "course",
        string="Course",
        related='assignment_id.course_id',
        readonly=True,
        store=True
    )

    status = fields.Selection(
        [
            ("pending","Pending"),
            ("submitted","Submitted"),
            ("late","Submitted Late"),
            ("evaluated","Evaluated")
        ],
        string = "Submission Status", 
        default='pending',
        required=True   
    )

    submitted_date = fields.Date(
        string = "Submission Date"
    )

    attachment = fields.Binary(
        string = "Submission File",
        attachment = True
    )

    attachment_filename = fields.Char(
        string = "Filename"
    )

    feedback = fields.Html(
        string = "Faculty Feedback"
    )

    evaluated_by = fields.Many2one(
        "res.users",
        string = "Evaluated By",
        readonly=True 
    )

    evaluated_date = fields.Date(
        string = "Evaluation Date",
        readonly=True 
    ) 

    notes = fields.Text(
        string = "Internal Notes"
    )

    @api.constrains("assignment_id","student_id")
    def _check_student_batch(self):
        for record in self:
            if record.assignment_id and record.student_id and record.student_id.batch_id != record.assignment_id.batch_id:
                raise ValidationError("The student must belong to the match assigned to this assignment")

    @api.constrains("status","submitted_date")
    def _check_submission_date(self):
        for record in self:
            if record.status in ("submitted","late","evaluated") and not record.submitted_date:
                raise ValidationError("Enter the submission date before marking the assignment as submitted or evaluated.")


    def action_mark_submitted(self):
        for record in self:
            if not record.submitted_date:
                record.submitted_date = fields.Date.today()

            deadline = record.assignment_id.deadline

            if deadline and record.submitted_date > deadline:
                record.status = "late"
            else:
                record.status = "submitted"

    def action_evaluate(self):
        for record in self:
            if not record.submitted_date:
                raise ValidationError("The assignment must be submitted before evaluation.")

            record.write({
                "status":"evaluated",
                "evaluated_by":self.env.user.id,
                "evaluated_date":fields.Date.today()
            })

