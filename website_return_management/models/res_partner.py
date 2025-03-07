# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Shijin V (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################


from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    return_order_count = fields.Integer(compute="_compute_returns",string='Return Orders')

    def _compute_returns(self):
        """Function to calculate the return count"""
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])
        sale_return_groups = self.env['sale.return'].sudo().read_group(
            domain=[('partner_id', '=', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id'])
        partners = self.browse()
        for group in sale_return_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.return_order_count += group['partner_id_count']
                    partners |= partner
                    partner= partner.parent_id
        (self - partners).return_order_count = 0

    def action_open_returns(self):
        """This function returns an action that displays the sale return orders from partner."""

        action = self.env['ir.actions.act_window']._for_xml_id('website_return_management.sale_return_action')
        domain = []
        if self.is_company:
            domain.append(('partner_id.commercial_partner_id.id', '=', self.id))
        else:
            domain.append(('partner_id.id', '=', self.id))
        action['domain'] = domain
        action['context'] = {'search_default_customer': 1}
        return action            