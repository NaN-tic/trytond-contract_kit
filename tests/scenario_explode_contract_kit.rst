=============================
Explode Contract Kit Scenario
=============================

.. Define contract with monthly periodicity
.. Start date = Start Period Date = Invoce Date.
.. Create Consumptions.
..      Check consumptions dates.
.. Create Invoice.
..      Check Invoice Lines Amounts
..      Check Invoice Date.

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

Create product uom::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])

Create products::

    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product1 = Product()
    >>> template1 = ProductTemplate()
    >>> template1.name = 'product1'
    >>> template1.default_uom = unit
    >>> template1.type = 'service'
    >>> template1.list_price = Decimal('0.0')
    >>> template1.cost_price = Decimal('0.0')
    >>> template1.account_expense = expense
    >>> template1.account_revenue = revenue
    >>> template1.customer_taxes.append(tax)
    >>> template1.save()
    >>> product1.template = template1
    >>> product1.kit = False
    >>> product1.save()
    >>> product2 = Product()
    >>> template2 = ProductTemplate()
    >>> template2.name = 'product2'
    >>> template2.default_uom = unit
    >>> template2.type = 'service'
    >>> template2.list_price = Decimal('0.0')
    >>> template2.cost_price = Decimal('0.0')
    >>> template2.account_expense = expense
    >>> template2.account_revenue = revenue
    >>> template2.save()
    >>> product2.template = template2
    >>> product2.kit = False
    >>> product2.save()

Create product kit::

    >>> product_kit = Product()
    >>> template_kit = ProductTemplate()
    >>> template_kit.name = 'product kit'
    >>> template_kit.default_uom = unit
    >>> template_kit.type = 'service'
    >>> template_kit.list_price = Decimal('40')
    >>> template_kit.cost_price = Decimal('25')
    >>> template_kit.account_expense = expense
    >>> template_kit.account_revenue = revenue
    >>> template_kit.save()
    >>> product_kit.template = template_kit
    >>> product_kit.kit = True
    >>> product_kit.kit_fixed_list_price = True
    >>> product_kit.explode_kit_in_contracts = True
    >>> product_kit.save()

Create kit lines::

    >>> KitLine = Model.get('product.kit.line')
    >>> kit_line1 = KitLine()
    >>> kit_line1.parent = product_kit
    >>> kit_line1.sequence = 1
    >>> kit_line1.product = product1
    >>> kit_line1.quantity = 1
    >>> kit_line1.unit = unit
    >>> kit_line1.unit_digits = 2
    >>> kit_line1.save()
    >>> kit_line2 = KitLine()
    >>> kit_line2.parent = product_kit
    >>> kit_line2.sequence = 1
    >>> kit_line2.product = product2
    >>> kit_line2.quantity = 1
    >>> kit_line2.unit = unit
    >>> kit_line2.unit_digits = 2
    >>> kit_line2.save()

Create payment term::

    >>> PaymentTerm = Model.get('account.invoice.payment_term')
    >>> payment_term = PaymentTerm(name='Term')
    >>> line = payment_term.lines.new(type='percent', ratio=Decimal(50))
    >>> delta = line.relativedeltas.new(days=20)
    >>> line = payment_term.lines.new(type='remainder')
    >>> delta = line.relativedeltas.new(days=40)
    >>> payment_term.save()
    >>> party.customer_payment_term = payment_term
    >>> party.save()

Create service::

    >>> Service = Model.get('contract.service')
    >>> service_kit = Service()
    >>> service_kit.name = 'Service Kit'
    >>> service_kit.product = product_kit
    >>> service_kit.freq = None
    >>> service_kit.save()
    >>> service = Service()
    >>> service.name = 'Service 1'
    >>> service.product = product1
    >>> service.freq = None
    >>> service.save()
    >>> service = Service()
    >>> service.name = 'Service 2'
    >>> service.product = product2
    >>> service.freq = None
    >>> service.save()


Create a contract::

    >>> Contract = Model.get('contract')
    >>> contract = Contract()
    >>> contract.party = party
    >>> contract.start_period_date = datetime.date(2015,01,05)
    >>> contract.freq = 'monthly'
    >>> contract.first_invoice_date = datetime.date(2015,02,04)
    >>> line = contract.lines.new()
    >>> line.service = service_kit
    >>> line.start_date = datetime.date(2015,01,05)
    >>> contract.save()
    >>> len(contract.lines)
    3
