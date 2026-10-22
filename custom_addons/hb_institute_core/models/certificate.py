from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import secrets
import base64
from io import BytesIO
import qrcode

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

    _verification_token_unique = models.Constraint(
        "UNIQUE(verification_token)",
        "Verification token must be unique"
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

    verification_token = fields.Char(
        string = "Verification Token",
        required=True, 
        readonly=True,
        copy=False,
        index=True,
        default = lambda self: secrets.token_urlsafe(32)
    )

    verification_url = fields.Char(
        string = "Verification URL",
        compute = "_compute_verification_url"
    )

    qr_code = fields.Binary(
        string = "Verification QR Code",
        compute = "_compute_qr_code"
    )

    @api.depends("verification_token")
    def _compute_verification_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param("web.base.url")
        for record in self:
            record.verification_url = (
                f"{base_url}/verify-certificate/{record.verification_token}"
                if base_url and record.verification_token
                else False
            )

    @api.depends("verification_token")
    def _compute_qr_code(self):
        for record in self:
            if not record.verification_url:
                record.qr_code = False
                continue
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4
            )

            qr.add_data(record.verification_url)
            qr.make(fit=True)

            image = qr.make_image(
                fill_color = "black",
                back_color = "white"
            )

            buffer = BytesIO()
            image.save(buffer,format="PNG") # type: ignore
            record.qr_code = base64.b64encode(buffer.getvalue())

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
        
