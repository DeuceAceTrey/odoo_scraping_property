from odoo import models, fields, api, tools

class property_avg_price_per_sqft_location(models.Model):
     _name = 'property_avg_price_per_sqft_location'

     _auto = False
     emirate = fields.Char()
     master_project = fields.Char()
     project = fields.Char()
     avg_price_sqft = fields.Float()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_avg_price_per_sqft_location as 
          (SELECT row_number() OVER () as id, sum(listing_price)/sum(listing_size) avg_price_sqft , emirate , master_project from property_property where listing_size > 0 group by emirate,master_project
          union all
          SELECT row_number() OVER () as id, sum(transaction_price)/sum(transaction_size) avg_price_sqft , emirate , master_project from property_property where transaction_size > 0 group by emirate,master_project
 )""")