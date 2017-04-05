# This file is part of the contract_kit module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval, Not

__all__ = ['Product']


class Product:
    __metaclass__ = PoolMeta
    __name__ = 'product.product'
    explode_kit_in_contracts = fields.Boolean('Explode in Contracts',
        states={
            'invisible': Not(Bool(Eval('kit'))),
            },
        depends=['kit'])

    @fields.depends('kit')
    def on_change_with_explode_kit_in_contracts(self, name=None):
        return True if self.kit else False

    @fields.depends('kit')
    def on_change_with_kit_fixed_list_price(self, name=None):
        return True if self.kit else False
