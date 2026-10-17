from odoo import api, fields, models

class AttendanceSummaryWizard(models.Model):
    _name = "attendance.summary.wizard"
    _description = "Attendance Summary Wizard"

    report_type = fields.Selection(
        [
            ("daily","Batch-wise Daily Attendance"),
            ("range","Date-range Attendance Summary"),
        ],
        string="Report Type",
        required=True,
        default="daily"
    )

    batch_id = fields.Many2one(
        "batch",
        string="Batch"
    )

    attendance_date = fields.Date(
        string="Attendance Date",
        default = fields.Date.context_today
    )

    date_from = fields.Date(
        string = "Start Date"
    )

    date_to = fields.Date(
        string = "End Date"
    )

    present_count = fields.Integer(
        string="Present",
        compute = "_compute_summary"
    )
    absent_count = fields.Integer(
        string="Absent",
        compute = "_compute_summary"
    )
    late_count = fields.Integer(
            string="Late",
            compute = "_compute_summary"
    )
    cancelled_count = fields.Integer(
        string="Cancelled",
        compute = "_compute_summary"
    )

    attendance_percentage = fields.Float(
        string = "Attendance Percentage",
        compute = "_compute_summary",
        digits=(16,2)
    )
    
    attendance_percentage_display = fields.Char(
        string="Attendance Percentage",
        compute="_compute_attendance_percentage_display"
    )

    @api.depends("attendance_percentage")
    def _compute_attendance_percentage_display(self):
        for wizard in self:
            wizard.attendance_percentage_display = (
                f"{wizard.attendance_percentage:.2f}%"
            )
        
    @api.depends("report_type","batch_id","attendance_date","date_from","date_to")
    def _compute_summary(self):
        Attendance = self.env['attendance']
        for wizard in self:
            wizard.present_count = 0
            wizard.absent_count = 0
            wizard.late_count = 0
            wizard.cancelled_count = 0
            wizard.attendance_percentage = 0.0

            domain = []

            if wizard.report_type == "daily":
                if not wizard.batch_id or not wizard.attendance_date:
                    continue
                domain += [
                    ("batch_id","=",wizard.batch_id.id),
                    ("attendance_date","=",wizard.attendance_date),
                ]

            elif wizard.report_type == "range":
                if (not wizard.date_from or not wizard.date_to or wizard.date_from > wizard.date_to):
                    continue
                domain += [
                    ("attendance_date",">=",wizard.date_from),
                    ("attendance_date","<=",wizard.date_to)
                ]
            
            records = Attendance.search(domain)

            wizard.present_count = len(records.filtered(lambda r: r.status == "present"))
            wizard.absent_count = len(records.filtered(lambda r: r.status == "absent"))
            wizard.late_count = len(records.filtered(lambda r: r.status == "late"))
            wizard.cancelled_count = len(records.filtered(lambda r: r.status == "cancelled"))

            eligible_count = (
                wizard.present_count + wizard.absent_count + wizard.late_count
            )

            if eligible_count:
                wizard.attendance_percentage = (
                    (wizard.present_count + wizard.late_count) / eligible_count
                ) * 100

    def action_generate_report(self):
        self.ensure_one()

        if self.report_type == "daily":
            if not self.batch_id or not self.attendance_date:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Missing Information",
                        "message": "Please select a batch and attendance date.",
                        "type": "warning",
                        "sticky": False,
                    },
                }

        elif self.report_type == "range":
            if not self.date_from or not self.date_to:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Missing Information",
                        "message": "Please select both dates.",
                        "type": "warning",
                        "sticky": False,
                    },
                }

            if self.date_from > self.date_to:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Invalid Date Range",
                        "message": "The start date must not be after the end date.",
                        "type": "warning",
                        "sticky": False,
                    },
                }

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Attendance Summary",
                "message": (
                    f"Present: {self.present_count}, "
                    f"Absent: {self.absent_count}, "
                    f"Late: {self.late_count}, "
                    f"Cancelled: {self.cancelled_count}, "
                    f"Attendance: {self.attendance_percentage:.2f}%"
                ),
                "type": "success",
                "sticky": True,
            },
        }