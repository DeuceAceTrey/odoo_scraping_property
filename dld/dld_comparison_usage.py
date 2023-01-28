from odoo import models, fields, api, tools

class property_dld_comparison_usage(models.Model):
     _name = 'property_dld_comparison_usage'

     _auto = False
     avg_price = fields.Float()
     usage = fields.Char()
     sqft_rate = fields.Float()
     pr_value = fields.Integer()
     emirate = fields.Char()

     #@api.cr  # cr
     def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view property_dld_comparison_usage as 
          (SELECT row_number() OVER () as id, sum(transaction_price)/sum(transaction_size) avg_price , usage , sum(transaction_size) sqft_rate, sum(transaction_price) pr_value, emirate  from property_property where origin='dubailand' group by usage , emirate)""")