from odoo import models, fields, api, tools

class property_avg_price_per_sqft_project(models.Model):
     _name = 'property_avg_price_per_sqft_project'

     _auto = False
     project = fields.Char()
     avg_price_sqft = fields.Float()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_avg_price_per_sqft_project as 
          (SELECT row_number() OVER () as id, sum(listing_price)/sum(listing_size) avg_price_sqft , project from property_property where listing_size > 0 group by project
          union all
          SELECT row_number() OVER () as id, sum(transaction_price)/sum(transaction_size) avg_price_sqft , project from property_property where transaction_size > 0 group by project
 )""")