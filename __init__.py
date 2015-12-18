# This file is part of the contract_kit module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .product import *
from .invoice import *
from .contract import *


def register():
    Pool.register(
        Product,
        InvoiceLine,
        ContractLine,
        module='contract_kit', type_='model')
