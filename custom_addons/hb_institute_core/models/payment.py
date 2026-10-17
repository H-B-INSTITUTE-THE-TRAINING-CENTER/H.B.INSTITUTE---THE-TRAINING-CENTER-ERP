from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Payment(models.Model):
    _name = "payment"
    _description = "Student Payment"

    name = fields.Char(
        string="Payment Reference",
        required=True,
        copy=False
    )

    fee_id = fields.Many2one(
        "fee",
        string="Fee",
        required=True,
        ondelete="restrict"
    )

    fee_balance = fields.Float(
        string = "Remaining Fee Balance",
        related = "fee_id.balance",
        readonly = True
    )

    student_id = fields.Many2one(
        "student",
        string="Student",
        required=True,
        ondelete="restrict"
    )

    payment_date = fields.Date(
        string="Payment Date",
        required=True,
        default=fields.Date.today
    )

    amount = fields.Float(
        string="Amount",
        required=True
    )

    payment_method = fields.Selection(
        [
            ("cash", "Cash"),
            ("upi", "UPI"),
            ("bank", "Bank Transfer"),
            ("cheque", "Cheque"),
            ("card", "Card"),
            ("other", "Other"),
        ], # type: ignore
        string="Payment Method",
        required=True
    )

    reference = fields.Char(
        string="Transaction / Cheque Reference"
    )

    note = fields.Text(
        string="Notes"
    )

    @api.onchange("fee_id")
    def _onchange_fee_id(self):
        if self.fee_id:
            self.student_id = self.fee_id.student_id # type: ignore
        else:
            self.student_id = False

    @api.constrains("student_id","fee_id")
    def _check_student_matches_fee(self):
        for record in self:
            if record.fee_id and record.student_id:
                if record.student_id != record.fee_id.student_id: # type: ignore
                    raise ValidationError(
                        "The selected Student must match the Stundet associated with the selected fee."
                    )

    
    @api.constrains("amount","fee_id")
    def _check_payment_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(
                    "Payment amount must be greater than zero."
                )
            if record.fee_id:
                other_payments = record.fee_id.payment_ids.filtered( # type: ignore
                    lambda payment: payment.id != record.id
                )

                total_paid = sum(other_payments.mapped("amount")) + record.amount

                if total_paid > record.fee_id.final_fees: # type: ignore
                    raise ValidationError(
                        "Payment amount cannot be greater than the remaining fee balance."
                    )

    

    