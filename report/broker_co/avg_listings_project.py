from odoo import models, fields, api, tools

class property_avg_listings_project(models.Model):
     _name = 'property_avg_listings_project'

     _auto = False
     broker_name = fields.Char()
     avg_listing_price = fields.Float()
     avg_count_per_project = fields.Float()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_avg_listings_project as 
          (SELECT row_number() OVER () as id,broker_name , COUNT(*) / COUNT(DISTINCT(project)) avg_count_per_project,SUM(listing_price)/Count(DISTINCT(project)) avg_listing_price FROM property_property GROUP BY broker_name ORDER BY broker_name DESC)""")