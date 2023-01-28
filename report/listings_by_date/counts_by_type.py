from odoo import models, fields, api, tools

class property_date_counts_per_type(models.Model):
     _name = 'property_date_counts_per_type'

     _auto = False
     listing_date = fields.Date()
     property_subtype = fields.Char()
     count = fields.Integer()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_date_counts_per_type as 
          (SELECT row_number() OVER () as id,listing_date , property_subtype , COUNT(*) count   FROM property_property WHERE listing_date IS NOT NULL GROUP BY listing_date , property_subtype )""")