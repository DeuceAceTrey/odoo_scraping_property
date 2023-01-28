from odoo import models, fields, api, tools

class property_furnished_price_project(models.Model):
     _name = 'property_furnished_price_project'

     _auto = False
     project = fields.Char()
     avg_price_sqft = fields.Float()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_furnished_price_project as 
          (SELECT row_number() OVER () as id, sum(listing_price)/sum(listing_size) avg_price_sqft , project from property_property where listing_size > 0 and furnished = true group by project
 )""")