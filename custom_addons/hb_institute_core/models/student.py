from odoo import models, fields


class Student(models.Model):
    _name = "student"
    _description = "Student"
    _rec_name = "name"

    # ---------------------------------------------------------
    # Personal Information
    # ---------------------------------------------------------


    name = fields.Char(
        string="Full Name",
        required=True,
    )

    date_of_birth = fields.Date(
        string = "Date Of Birth"
    )

    gender = fields.Selection(
        selection = [
            ("male","Male"),
            ("female","Female"),
            ("other","Other")
        ],
        string = "Gender"
    )

    photo = fields.Image(
        string = "Photo"   
    )
    
    # ---------------------------------------------------------
    # Contact Information
    # ---------------------------------------------------------
    
    mobile = fields.Char(
        string="Mobile",
        required = True
    )

    alternate_mobile = fields.Char(
        string = "Alternative Mobile"
    )

    email = fields.Char(
        string="Email",
        required = True
    )

    address = fields.Text(
        string = "Address"
    )
    
    # ---------------------------------------------------------
    # Guardian Information
    # ---------------------------------------------------------

    guardian_name = fields.Char(
        string = "Guardian Name"
    )

    guardian_mobile = fields.Char(
        string = "Guardian Mobile"
    )

    guardian_relation = fields.Char(
        string = "Relationship"
    )

    # ---------------------------------------------------------
    # Admission Information
    # ---------------------------------------------------------



    admission_date = fields.Date(
        string="Admission Date",
        default = fields.Date.today
    )

    status = fields.Selection(
        selection = [
            ("inquiry","Inquiry"),
            ("active","Active"),
            ("completed","Completed"),
            ("dropped","Dropped"),
            ("placed","Placed")
        ],
        string = "Status",
        default = "inquiry",
        required = False
    )

    notes = fields.Text(
        string = "Notes"
    )

    # ---------------------------------------------------------
    # System Information
    # ---------------------------------------------------------


    active = fields.Boolean(
        string="Active",
        default=True,
    )

    course_id = fields.Many2one(
        "course",
        string = "Course"
    )

    batch_id = fields.Many2one(
        "batch",
        string = "Batch"
    )

    enrollment_ids = fields.One2many(
        "enrollment",
        "student_id",
        string = "Enrollments"
    )