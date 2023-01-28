from odoo import models, fields, api, tools

class property_type_price_range(models.Model):
     _name = 'property_type_price_range'

     _auto = False
     property_subtype = fields.Char()
     max_price = fields.Integer()
     min_price = fields.Integer()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_type_price_range as 
          (SELECT row_number() OVER () as id, max(listing_price) max_price , min(listing_price) min_price, property_subtype from property_property where origin != 'dubailiand' group by property_subtype
 )""")