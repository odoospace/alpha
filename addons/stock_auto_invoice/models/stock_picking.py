# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3).

from openerp import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def generate_invoice(self):
        if self.sale_id:
            if not self.sale_id.invoice_ids:
                res = self.sale_id.action_invoice_create(False, True)
                print res
                invoice = self.env['account.invoice'].browse(res)
                invoice.signal_workflow('invoice_open')

