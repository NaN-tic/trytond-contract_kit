# This file is part of the contract_kit module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase
import trytond.tests.test_tryton
import unittest


class ContractKitTestCase(ModuleTestCase):
    'Test Contract Kit module'
    module = 'contract_kit'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ContractKitTestCase))
    return suite
