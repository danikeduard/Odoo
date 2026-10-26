from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    member_ids = fields.One2many("library.member", "partner_id")
    member_count = fields.Integer(
        compute="_compute_member_count",
        compute_sudo=True,
    )

    @api.depends("member_ids")
    def _compute_member_count(self):
        for partner in self:
            partner.member_count = len(partner.member_ids)

    def action_view_library_member(self):
        self.ensure_one()
        member = self.member_ids[:1]
        return {
            "type": "ir.actions.act_window",
            "name": "Читач",
            "res_model": "library.member",
            "view_mode": "form",
            "views": [
                (self.env.ref("library_rental.view_library_member_form").id, "form")
            ],
            "res_id": member.id,
            "target": "current",
        }
