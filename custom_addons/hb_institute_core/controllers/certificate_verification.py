from odoo import http
from odoo.http import request

class CertificateVerificationController(http.Controller):
    @http.route(
        "/verify-certificate/<string:token>",
        type="http",
        auth="public",
        website=True,
        sitemap=False
    )
    def verify_certificate(self, token, **kwargs):
        certficate = request.env['certificate'].sudo().search(
            [("verificate_token","=",token)],
            limit=1
        )

        values = {
            "certificate":certficate,
            "verification_result":"not_found"
        }

        if certficate:
            if certficate.status == "issued":
                values["verification_result"] = "valid"
            elif certficate.status == "revoked":
                values['verification_result'] = "revoked"
            else:
                # Draft certificates are not disclosed publicly.
                values['certificate'] = False

        return request.render(
            "hb_institute_core.certificate_verification_page",
            values
        )