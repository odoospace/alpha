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
                return invoice.invoice_print()
                
            else:
                print 'entro otro', self.sale_id.invoice_ids[0]

                return self.sale_id.invoice_ids[0].invoice_print()

                # print 'context',self._context

                # context = self._context.copy()
                # context.update({'default_type': 'out_invoice'})
                # context.update({'type': 'out_invoice'})
                # context.update({'journal_type': 'sale'})
                # print 'post-context', context

                # print self.sale_id.invoice_ids[0].read() 

                # self.env.context = context
                # data = {}
                # data['ids'] = [self.sale_id.invoice_ids[0].id]
                # data['model'] = 'account.invoice'
                # data['form'] = self.sale_id.invoice_ids[0].read()[0]
                

                # return self.env['report'].get_action(self.sale_id.invoice_ids[0], 'account.report_invoice', data)
                # # return self.env['report'].get_action(self.sale_id.invoice_ids[0], 'account.report_invoice')






