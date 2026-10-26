from . import models


def post_init_hook(env):
    Member = env["library.member"]
    Partner = env["res.partner"]
    for member in Member.search([("partner_id", "=", False)]):
        partner = Partner.search(
            [("email", "=", member.email)],
            limit=1,
        ) if member.email else Partner
        if not partner:
            partner = Partner.create(
                {
                    "name": member.name,
                    "email": member.email,
                    "phone": member.phone,
                }
            )
        member.partner_id = partner
