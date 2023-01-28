from odoo import models, fields, api, tools

class property_dld_avg_price_landmark(models.Model):
     _name = 'property_dld_avg_price_landmark'

     _auto = False
     avg_price = fields.Float()
     nearest_landmark = fields.Char()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_dld_avg_price_landmark as 
          (SELECT row_number() OVER () as id, sum(transaction_price)/sum(transaction_size) avg_price , nearest_landmark from property_property where origin='dubailand' group by nearest_landmark
 )""")