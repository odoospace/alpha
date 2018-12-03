# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3).

from openerp import models, fields, api, _
from openerp.tools import float_compare
from openerp.exceptions import UserError

class stock_immediate_transfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    @api.multi
    def process(self):
        self.ensure_one()
        # If still in draft => confirm and assign
        if self.pick_id.state == 'draft':
            self.pick_id.action_confirm()
            if self.pick_id.state != 'assigned':
                self.pick_id.action_assign()
                if self.pick_id.state != 'assigned':
                    raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
        for pack in self.pick_id.pack_operation_ids:
            if pack.product_qty > 0:
                pack.write({'qty_done': pack.product_qty})
            else:
                pack.unlink()
        self.pick_id.do_transfer()

        if self.pick_id.sale_id:
            if not self.pick_id.sale_id.invoice_ids:
                res = self.pick_id.sale_id.action_invoice_create(False, True)
                invoice = self.env['account.invoice'].browse(res)
                invoice.signal_workflow('invoice_open')
                domain = [('name','=','Invoice - Send by Email')]
                template = self.env['mail.template'].search(domain, limit=1)
                template = template[0]
                print(template.email_to)
                template.send_mail(invoice.id, True)
                #return invoice.invoice_print()
            else:
                domain = [('name','=','Invoice - Send by Email')]
                template = self.env['mail.template'].search(domain, limit=1)
                template = template[0]
                template.send_mail(self.pick_id.sale_id.invoice_ids[0].id, True)
                #return self.pick_id.sale_id.invoice_ids[0].invoice_print()
        return

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def generate_invoice(self):
        if self.sale_id:
            if not self.sale_id.invoice_ids:
                return
            else:
                return self.sale_id.invoice_ids[0].invoice_print()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def open_payment_create(self):
        context = {
            'default_payment_type': 'inbound',
            'default_partner_type': 'customer',
            'default_partner_id': self.partner_id.id,
            'default_amount': self.amount_total,
            'default_communication': self.name,
            'default_journal_id': self.payment_mode_id.fixed_journal_id.id
        }
        return {
            'name': 'Register Payment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'view_id': 398,
            'type': 'ir.actions.act_window',
            'res_id': False,
            'context': context,
        }
