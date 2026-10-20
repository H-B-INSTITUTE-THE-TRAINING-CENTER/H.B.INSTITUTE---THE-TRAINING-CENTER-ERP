from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class Certificate(models.Model):
    _name = "certificate"
    _description = "Student Course Certificate"
    _order = "certificate_date desc, id desc"
    _rec_name = "certificate_number"

    _number_unique = models.Constraint(
        "UNIQUE(certificate_number)",
        "Certificate number must be unique."
    )

    _enrollment_unique = models.Constraint(
        "UNIQUE(enrollment_id)",
        "A certificate already exists for this enrollment."
    )

    certificate_number = fields.Char(
        string="Certificate Number",
        required=True, 
        readonly=True,
        copy=False,
        default='New',
        index=True
    )

    enrollment_id = fields.Many2one(
        "enrollment",
        string="Enrollment",
        required=True, 
        ondelete='restrict', 
        index=True
    )

    student_id = fields.Many2one(
        "student",
        string="Student",
        related='enrollment_id.student_id',
        readonly=True,
        store=True   
    )

    course_id = fields.Many2one(
        "course",
        string = "Course",
        related='enrollment_id.course_id',
        readonly=True,
        store=True
    )

    batch_id = fields.Many2one(
        "batch",
        string = "Batch", 
        related='enrollment_id.batch_id',
        readonly=True,
        store=True
    )

    certificate_date = fields.Date(
        string = "Certificate Date",
        required = True,
        default = fields.Date.today
    )

    status = fields.Selection(
        [
            ("draft","Draft"),
            ("issued","Issued"),
            ("revoked","Revoked")
        ],
        string = "Status", 
        required=True, 
        default='draft',
        copy=False
    )

    notes = fields.Text(string = "Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("certificate_number","New") == "New":
                vals["certificate_number"] = (self.env["ir.sequence"].next_by_code("certificate.sequence") or "New")
        
        return super().create(vals_list)

    @api.constrains("enrollment_id")
    def _check_completed_enrollment(self):
        for record in self:
            if record.enrollment_id and record.enrollment_id.status != "completed":
                raise ValidationError("A certificate can only be created for a completed enrollment. ")

    def action_issue(self):
        for record in self:
            if record.status != "draft":
                raise UserError("Only draft certificates can be issued.")
            
            if record.enrollment_id.status != "completed":
                raise UserError("The enrollment must be complete before issuing the certificate.")

            record.status = "issued"

    def action_revoke(self):
        for record in self:
            if record.status != "issued":
                raise UserError("Only issued certificates can be revoked.")
            
            record.status = "revoked"

    def action_reset_to_draft(self):
        for record in self:
            if record.status != "revoked":
                raise UserError("Only revoked certificates can be reset to draft.")
            
            record.status = "draft"


    def action_print_certificate(self):
        self.ensure_one()

        if self.status != "issued":
            raise UserError("Only issued certificates can be printed.")

        return self.env.ref("hb_institute_core.action_report_certificate").report_action(self)
        
