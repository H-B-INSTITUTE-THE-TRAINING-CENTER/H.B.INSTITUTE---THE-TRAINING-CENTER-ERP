# pyright: reportUnusedExpression=false

{
    "name": "H.B.INSTITUTE Core",
    "version": "1.0.0",
    "summary": "Core education management for H.B.INSTITUTE",
    "description": """
        H.B.INSTITUTE ERP
        =================

        Core education management module for
        H.B.INSTITUTE - THE TRAINING CENTER.
    """,
    "category": "Education",
    "author": "H.B.INSTITUTE - THE TRAINING CENTER",
    "website": "https://hbinstitute.co.in/",
    "license": "LGPL-3",
    "depends": [
        "base",
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/enrollment_sequence.xml',
        'views/student_views.xml',
        'views/course_views.xml',
        'views/batch_views.xml',
        'views/enrollment_views.xml',
        "views/fee_views.xml",
        "views/payment_views.xml",
        "reports/payment_receipt_report.xml",
        "report/payment_receipt_templates.xml",
        "views/attendance_views.xml",
        "views/attendance_summary_views.xml",
        "views/assignment_views.xml",
        "views/examination_views.xml",
        "data/certificate_sequence.xml",
        "reports/certificate_paperformat.xml",
        "views/certificate_views.xml",
        "reports/certificate_report.xml",
        "report/certificate_templates.xml",
    ],
    "installable": True,
    "application": True,
}