from odoo import models, fields, api, tools

class property_dld_avg_sale_price_project_date(models.Model):
     _name = 'property_dld_avg_sale_price_project_date'

     _auto = False
     avg_price = fields.Float()
     project = fields.Char()
     transaction_date = fields.Date()

     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_dld_avg_sale_price_project_date as 
          (SELECT row_number() OVER () as id, sum(transaction_price)/sum(transaction_size) avg_price , project , transaction_date from property_property where origin='dubailand' and usage='Commercial' group by project , transaction_date)""")