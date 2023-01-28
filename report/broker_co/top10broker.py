from odoo import models, fields, api, tools

class property_top10broker(models.Model):
     _name = 'property_top10broker'

     _auto = False
     broker_name = fields.Char()
     listing_count = fields.Integer()
     sum_listing_price = fields.Integer()



     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_top10broker as 
          (SELECT row_number() OVER () as id,broker_name , COUNT(*) listing_count , SUM(listing_price) sum_listing_price FROM property_property GROUP BY broker_name ORDER BY listing_count DESC)""")