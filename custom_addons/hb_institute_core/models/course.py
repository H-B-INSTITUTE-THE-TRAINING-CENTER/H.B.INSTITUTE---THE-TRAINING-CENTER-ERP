from odoo import models, fields

class Course(models.Model):
    _name = "course"
    _description = "Training Course"
    _order = "name"

    name = fields.Char(
        string = "Course Name",
        required = True
    )

    code = fields.Char(
        string = "Course Code",
        required = True
    )

    duration = fields.Char(
        string = "Duration"
    )

    fees = fields.Float(
        string = "Course Fees"
    )

    description = fields.Text(
        string = "Description"
    )

    active = fields.Boolean(
        string = "Active",
        default = True
    )

    student_ids = fields.One2many(
        "student",
        "course_id",
        string = "Students"
    )

    enrollment_ids = fields.One2many(
        "enrollment",
        "course_id",
        string = "Enrollments"
    )
