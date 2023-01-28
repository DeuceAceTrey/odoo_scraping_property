from odoo import models, fields, api, tools

class property_broker_listingdate(models.Model):
     _name = 'property_broker_listingdate'

     _auto = False
     broker_name = fields.Char()
     listing_count = fields.Integer()
     listing_date = fields.Date()



     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_broker_listingdate as 
          (SELECT row_number() OVER () as id,broker_name , COUNT(*) listing_count , listing_date FROM property_property GROUP BY broker_name , listing_date ORDER BY listing_date DESC)""")