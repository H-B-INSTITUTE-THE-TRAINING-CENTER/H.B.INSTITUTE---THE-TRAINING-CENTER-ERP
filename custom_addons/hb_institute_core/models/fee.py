from odoo import models, fields, api

class Fee(models.Model):
    _name = "fee"
    _description = "Student Fee"

    _sql_constraints = [
        (
            "unique_enrollment_fee",
            "unique(enrollment_id)",
            "A fee record already exists for this enrollment."
        )
    ]

    name = fields.Char(
        string="Fee Reference",
        required = True,
        copy = False
    )

    student_id = fields.Many2one(
        "student",
        string = "Student",
        required = True,
        ondelete = "restrict"
    )

    enrollment_id = fields.Many2one(
        "enrollment",
        string = "Enrollment",
        required = True,
        ondelete = "restrict"
    )

    total_fees = fields.Float(
        string = "Total Fees",
        required = True
    )

    discount = fields.Float(
        string="Discount"
    )

    final_fees = fields.Float(
        string = "Final Fees",
        compute = "_compute_final_fees",
        store = True
    )

    amount_paid = fields.Float(
        string = "Amount Paid",
        compute = "_compute_payment_details",
        store = True
    )

    balance = fields.Float(
        string = "Balance",
        compute = "_compute_payment_details",
        store = True
    )

    payment_status = fields.Selection(
        [
            ("pending","Pending"),
            ("partial","Partial"),
            ("paid","Paid")
        ], # type: ignore
        string = "Payment Status",
        compute = "_compute_payment_details",
        store = True

    )

    notes = fields.Text(
        string = "Notes"
    )

    payment_ids = fields.One2many(
        "payment",
        "fee_id",
        string = "Payments"
    )

    @api.depends("total_fees","discount")
    def _compute_final_fees(self):
        for record in self:
            record.final_fees = record.total_fees - record.discount
    
    @api.depends("final_fees","payment_ids.amount")
    def _compute_payment_details(self):
        for record in self:
            amount_paid = sum(record.payment_ids.mapped("amount")) # type: ignore
            record.amount_paid = amount_paid
            record.balance = record.final_fees - amount_paid

            if amount_paid <= 0:
                record.payment_status = "pending"
            elif amount_paid < record.final_fees:
                record.payment_status = "partial"
            else:
                record.payment_status = "paid"

            
