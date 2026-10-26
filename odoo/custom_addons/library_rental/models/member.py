from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LibraryMember(models.Model):
    _name = "library.member"
    _description = "Library Member"
    _order = "name"

    name = fields.Char(related="partner_id.name", store=True, readonly=False)
    card_number = fields.Char(string="Номер читацького квитка", required=True)
    email = fields.Char(related="partner_id.email", readonly=False)
    phone = fields.Char(related="partner_id.phone", readonly=False)
    partner_id = fields.Many2one(
        "res.partner",
        string="Контакт",
        ondelete="restrict",
        copy=False,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Користувач Odoo",
        ondelete="set null",
        copy=False,
    )
    loan_ids = fields.One2many("library.loan", "member_id", string="Видачі")

    _sql_constraints = [
        (
            "library_member_card_number_uniq",
            "unique(card_number)",
            "Номер читацького квитка має бути унікальним.",
        ),
        (
            "user_id_uniq",
            "unique(user_id)",
            "Цей користувач Odoo уже привʼязаний до іншого читача.",
        ),
        (
            "partner_id_uniq",
            "unique(partner_id)",
            "Цей контакт уже привʼязаний до іншого читача.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = []
        for incoming_vals in vals_list:
            vals = dict(incoming_vals)
            partner = self.env["res.partner"].browse(vals.get("partner_id")).exists()
            user = self.env["res.users"].browse(vals.get("user_id")).exists()
            if not partner and vals.get("user_id"):
                partner = user.partner_id if user else self.env["res.partner"]
            if partner and not user:
                user = self.env["res.users"].search(
                    [("partner_id", "=", partner.id)],
                    limit=1,
                )
                if user:
                    vals["user_id"] = user.id
            if not partner:
                partner_name = vals.get("name")
                if not partner_name:
                    raise ValidationError(
                        _("Не вдалося визначити контакт або імʼя читача.")
                    )
                partner = self.env["res.partner"].create(
                    {
                        "name": partner_name,
                        "email": vals.get("email"),
                        "phone": vals.get("phone"),
                    }
                )
            vals["partner_id"] = partner.id
            prepared_vals_list.append(vals)
        return super().create(prepared_vals_list)

    def write(self, vals):
        vals = dict(vals)
        if vals.get("partner_id") and not vals.get("user_id"):
            user = self.env["res.users"].search(
                [("partner_id", "=", vals["partner_id"])],
                limit=1,
            )
            if user:
                vals["user_id"] = user.id
        return super().write(vals)

    @api.constrains("user_id", "partner_id")
    def _check_user_partner(self):
        for member in self:
            if (
                member.user_id
                and member.partner_id
                and member.partner_id != member.user_id.partner_id
            ):
                raise ValidationError(
                    "Контакт читача має збігатися з контактом привʼязаного користувача"
                )

    @api.onchange("user_id")
    def _onchange_user_id(self):
        if self.user_id and not self.partner_id:
            self.partner_id = self.user_id.partner_id

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id and not self.user_id:
            self.user_id = self.env["res.users"].search(
                [("partner_id", "=", self.partner_id.id)],
                limit=1,
            )
