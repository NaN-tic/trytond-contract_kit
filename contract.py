# This file is part of the contract_kit module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


__all__ = ['ContractLine']
__metaclass__ = PoolMeta


class ContractLine:
    __name__ = 'contract.line'
    kit_depth = fields.Integer('Depth', required=True,
        help='Depth of the line if it is part of a kit.')
    kit_parent_line = fields.Many2One('contract.line', 'Parent Kit Line',
        help='The kit that contains this product.')
    kit_child_lines = fields.One2Many('contract.line', 'kit_parent_line',
        'Lines in the kit', help='Subcomponents of the kit.')
    product = fields.Function(fields.Many2One('product.product', 'Product'),
        'get_product', searcher='search_product')

    @classmethod
    def __setup__(cls):
        super(ContractLine, cls).__setup__()
        cls._error_messages.update({
                'kit_without_service_error': 'Product %s of kit has not any '
                    'service related.',
                })

    @classmethod
    def default_kit_depth(cls):
        return 0

    def get_product(self, name=None):
        if self.service and self.service.product:
            return self.service.product.id

    @classmethod
    def search_product(cls, name, clause):
        return [('service.' + name,) + tuple(clause[1:])]

    @classmethod
    def explode_kit(cls, lines):
        '''
        Walks through the Kit tree in depth-first order and returns
        a sorted list with all the components of the product.
        '''
        Service = Pool().get('contract.service')

        sequence = lines[0].sequence if lines and lines[0].sequence else 1
        to_write, to_create = [], []
        for line in lines:
            if line.sequence != sequence and to_create:
                line.sequence = sequence
            sequence += 1
            depth = line.kit_depth + 1
            if (line.product and line.product.kit and line.product.kit_lines
                    and line.product.explode_kit_in_contracts):
                kit_lines = list(line.product.kit_lines)
                kit_lines = zip(kit_lines, [depth] * len(kit_lines))
                while kit_lines:
                    kit_line = kit_lines.pop(0)
                    kit_line, depth = kit_line[0], kit_line[1]
                    services = Service.search([
                            ('product', '=', kit_line.product.id),
                            ], limit=1)
                    if not services:
                        cls.raise_user_error('kit_without_service_error',
                            (kit_line.product.name,))
                    else:
                        service, = services
                    contract_line = cls()
                    contract_line.contract = line.contract
                    contract_line.service = service
                    contract_line.start_date = line.start_date
                    contract_line.end_date = line.end_date
                    contract_line.description = ''
                    contract_line.unit_price = (
                        service.product.template.list_price)
                    contract_line.on_change_service()
                    contract_line.description = ('%s%s' %
                        ('> ' * depth, contract_line.description)
                        if contract_line.description else ' ')
                    contract_line.first_invoice_date = line.first_invoice_date
                    contract_line.sequence = sequence
                    contract_line.kit_depth = depth
                    contract_line.kit_parent_line = line

                    to_create.append(contract_line._save_values)
                if not line.product.kit_fixed_list_price and line.unit_price:
                    line.unit_price = Decimal('0.0')
        if to_write:
            cls.write(*to_write)
        return super(ContractLine, cls).create(to_create)

    def get_kit_lines(self, kit_line=None):
        res = []
        if kit_line:
            childs = kit_line.kit_child_lines
        else:
            childs = self.kit_child_lines
        for kit_line in childs:
            res.append(kit_line)
            res += self.get_kit_lines(kit_line)
        return res

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        default.setdefault('kit_child_lines', [])
        new_lines, no_kit_lines = [], []
        copied_parents = set()
        with Transaction().set_context(explode_kit=False):
            for line in lines:
                if line.kit_child_lines:
                    if line.kit_parent_line not in copied_parents:
                        new_line, = super(ContractLine, cls).copy([line],
                            default)
                        new_lines.append(new_line)
                        copied_parents.add(line.id)
                        new_default = default.copy()
                        new_default['kit_parent_line'] = new_line.id
                        super(ContractLine, cls).copy(line.kit_child_lines,
                            default=new_default)
                elif (line.kit_parent_line and
                        line.kit_parent_line.id in copied_parents):
                    # Already copied by kit_child_lines
                    continue
                else:
                    no_kit_lines.append(line)
            new_lines += super(ContractLine, cls).copy(no_kit_lines,
                default=default)
        return new_lines

    @classmethod
    def create(cls, vlist):
        lines = super(ContractLine, cls).create(vlist)
        if Transaction().context.get('explode_kit', True):
            lines.extend(cls.explode_kit(lines))
        return lines

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        to_write, to_reset, to_delete = [], [], []
        if Transaction().context.get('explode_kit', True):
            for lines, values in zip(actions, actions):
                reset_kit = False
                if ('service' in values or 'first_invoice_date' in values
                        or 'start_date' in values):
                    reset_kit = True
                lines = lines[:]
                if reset_kit:
                    for line in lines:
                        to_delete += line.get_kit_lines()
                    lines = list(set(lines) - set(to_delete))
                    to_reset.extend(lines)
                to_write.extend((lines, values))
        else:
            to_write = args
        super(ContractLine, cls).write(*to_write)
        if to_delete:
            cls.delete(to_delete)
        if to_reset:
            cls.explode_kit(to_reset)

    def get_invoice_line(self, invoice_type):
        lines = super(ContractLine, self).get_invoice_line(invoice_type)
        for line in lines:
            line.sequence = self.sequence
        return lines
