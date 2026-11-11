from odoo import api, fields, models


class LibraryReturnWizard(models.TransientModel):
    _name = "library.return.wizard"
    _description = "Оформлення повернення"

    loan_id = fields.Many2one("library.loan", required=True)
    condition_on_return = fields.Selection(
        selection=lambda self: self.env["library.copy"]._fields["state"].selection,
        required=True,
    )
    notes = fields.Text()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "library.loan":
            res["loan_id"] = self.env.context.get("active_id")
        return res

    def action_confirm(self):
        self.ensure_one()
        self.loan_id.with_context(library_rental_sync=True).write(
            {
                "state": "returned",
                "return_date": fields.Date.today(),
            }
        )
        self.loan_id.copy_id.state = self.condition_on_return
        return {"type": "ir.actions.act_window_close"}
