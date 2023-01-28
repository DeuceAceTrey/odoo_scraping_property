from odoo import models, fields, api, tools

class property_broker_exclusive(models.Model):
     _name = 'property_broker_exclusive'

     _auto = False
     broker_name = fields.Char()
     exclusive_count = fields.Integer()


     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_broker_exclusive as 
          (SELECT row_number() OVER () as id,broker_name , COUNT(*) exclusive_count  FROM property_property WHERE exclusive=true GROUP BY broker_name )""")