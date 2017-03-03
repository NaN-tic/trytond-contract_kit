============
Contract Kit
============

"""
Create a contract with monthly periodicity, kit and fixed price
Create a contract with monthly periodicity, kit and not fixed price
"""

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> from.trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences
    >>> today = datetime.datetime.combine(datetime.date.today(),
    ...     datetime.datetime.min.time())
    >>> tomorrow = datetime.date.today() + relativedelta(days=1)

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install contract_kit::

    >>> Module = Model.get('ir.module')
    >>> contract_module, = Module.find([('name', '=', 'contract_kit')])
    >>> Module.install([contract_module.id], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']

Get Journal::

    >>> Journal = Model.get('account.journal')
    >>> journal_revenue, = Journal.find([('code', '=', 'REV')], limit=1)

Create tax::

    >>> tax = set_tax_code(create_tax(Decimal('.10')))
    >>> tax.save()
    >>> invoice_base_code = tax.invoice_base_code
    >>> invoice_tax_code = tax.invoice_tax_code
    >>> credit_note_base_code = tax.credit_note_base_code
    >>> credit_note_tax_code = tax.credit_note_tax_code

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Configure unit to accept decimals::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> unit.rounding =  0.01
    >>> unit.digits = 2
    >>> unit.save()

Create products::

    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.cost_price = Decimal('25')
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> product.template = template
    >>> product.save()

    >>> product1 = Product()
    >>> template1 = ProductTemplate()
    >>> template1.name = 'product1'
    >>> template1.default_uom = unit
    >>> template1.type = 'service'
    >>> template1.list_price = Decimal('10')
    >>> template1.cost_price = Decimal('5')
    >>> template1.account_expense = expense
    >>> template1.account_revenue = revenue
    >>> template1.save()
    >>> product1.template = template1
    >>> product1.save()

    >>> product2 = Product()
    >>> template2 = ProductTemplate()
    >>> template2.name = 'product2'
    >>> template2.default_uom = unit
    >>> template2.type = 'service'
    >>> template2.list_price = Decimal('20')
    >>> template2.cost_price = Decimal('15')
    >>> template2.account_expense = expense
    >>> template2.account_revenue = revenue
    >>> template2.save()
    >>> product2.template = template2
    >>> product2.save()

Create product kit::

    >>> product.kit = True
    >>> product.kit_fixed_list_price = True
    >>> product.explode_kit_in_contracts = True
    >>> line = product.kit_lines.new()
    >>> line.product = product1
    >>> line.quantity = 1
    >>> line.unit = unit
    >>> line.sequence = 1
    >>> line2 = product.kit_lines.new()
    >>> line2.product = product2
    >>> line2.quantity = 1
    >>> line2.unit = unit
    >>> line2.sequence = 2
    >>> product.save()

Create payment term::

    >>> PaymentTerm = Model.get('account.invoice.payment_term')
    >>> payment_term = PaymentTerm(name='Term')
    >>> line = payment_term.lines.new(type='percent', percentage=Decimal(50))
    >>> delta = line.relativedeltas.new(days=20)
    >>> line = payment_term.lines.new(type='remainder')
    >>> delta = line.relativedeltas.new(days=40)
    >>> payment_term.save()
    >>> party.customer_payment_term = payment_term
    >>> party.save()

Configuration contract::

    >>> ContractConfiguration = Model.get('contract.configuration')
    >>> configuration, = ContractConfiguration.find([])
    >>> configuration.journal = journal_revenue
    >>> configuration.save()

Create monthly service::

    >>> Service = Model.get('contract.service')
    >>> service = Service()
    >>> service.name = 'Service Kit'
    >>> service.product = product
    >>> service.freq = None
    >>> service.save()

    >>> service1 = Service()
    >>> service1.name = 'Service product1'
    >>> service1.product = product1
    >>> service1.freq = None
    >>> service1.save()

    >>> service2 = Service()
    >>> service2.name = 'Service product2'
    >>> service2.product = product2
    >>> service2.freq = None
    >>> service2.save()

Create a contract kit and fixed price::

    >>> Contract = Model.get('contract')
    >>> contract = Contract()
    >>> contract.party = party
    >>> contract.start_period_date = datetime.date(2015, 01, 01)
    >>> contract.freq = 'monthly'
    >>> contract.interval = 1
    >>> contract.first_invoice_date = datetime.date(2015, 02, 01)
    >>> line = contract.lines.new()
    >>> line.start_date = datetime.date(2015, 01, 01)
    >>> line.service = service
    >>> line.unit_price
    Decimal('40')
    >>> contract.save()
    >>> len(contract.lines)
    3
    >>> line1, line2, line3 = contract.lines
    >>> line1.unit_price
    Decimal('0.0')
    >>> line2.unit_price
    Decimal('0.0')
    >>> line3.unit_price
    Decimal('40')

Create a contract kit and not fixed price::

    >>> product.kit_fixed_list_price = False
    >>> product.save()
    >>> product.reload()

    >>> contract = Contract()
    >>> contract.party = party
    >>> contract.start_period_date = datetime.date(2015, 01, 01)
    >>> contract.freq = 'monthly'
    >>> contract.interval = 1
    >>> contract.first_invoice_date = datetime.date(2015, 02, 01)
    >>> line = contract.lines.new()
    >>> line.start_date = datetime.date(2015, 01, 01)
    >>> line.service = service
    >>> line.unit_price
    Decimal('40')
    >>> contract.save()
    >>> len(contract.lines)
    3
    >>> line1, line2, line3 = contract.lines
    >>> line1.unit_price
    Decimal('10')
    >>> line2.unit_price
    Decimal('20')
    >>> line3.unit_price
    Decimal('0.0')
