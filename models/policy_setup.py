from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Policy_Info(models.Model):
    _name ="insurance.line.business"
    _rec_name = 'line_of_business'

    insurance_type = fields.Selection([('life', 'Life'),
                          ('p&c', 'P&C'),
                          ('health', 'Health'), ],
                         'Insured Type', track_visibility='onchange', required=True)
    line_of_business = fields.Char(string='Line of Business', required=True)
    object= fields.Selection([('person', 'Person'),
                          ('vehicle', 'Vehicle'),
                          ('cargo', 'Cargo'),
                          ('location', 'Location'),],
                         'Insured Object', track_visibility='onchange', required=True)
    desc = fields.Char(string='Description')


class Product(models.Model):
    _name='insurance.product'
    _rec_name = 'product_name'

    product_name=fields.Char('Product Name',required=True)
    insurer=fields.Many2one('res.partner', string="Insurer",domain="[('insurer_type','=',1)]")
    line_of_bus=fields.Many2one('insurance.line.business','Line of Business')
    income_account=fields.Many2one('account.account','Income Account')
    expense_account = fields.Many2one('account.account','Expense Account')
    coverage=fields.One2many('insurance.product.coverage','product_id',string='Coverage')
    brokerage=fields.One2many('insurance.product.brokerage','product_id',string='Brokerage')
    commision_id = fields.One2many("commision.setup","policy_relation_id")

class coverage(models.Model):
    _name='insurance.product.coverage'

    Name=fields.Char('Cover Name')
    defaultvalue=fields.Char('Default Sum Insured')
    required=fields.Boolean('Required')
    deductible = fields.Integer('Deductible')
    limitone=fields.Integer('Limit in One')
    limittotal=fields.Integer('Limit in Total')
    readonly=fields.Boolean('Read Only')
    product_id=fields.Many2one('insurance.product')
    lop_id=fields.Many2one('insurance.line.business',string='Line of Business')


class Brokerage(models.Model):
    _name='insurance.product.brokerage'

    datefrom=fields.Date('Date from')
    dateto=fields.Date('Date to')
    basic_commission = fields.Float('Basic Commission')
    complementary_commission = fields.Float('Complementary Commission')
    early_collection = fields.Float('Early Collection Commission')
    fixed_commission = fields.Monetary(default=0.0, currency_field='company_currency_id',string='Fixed Commission')
    company_currency_id = fields.Many2one('res.currency', related='product_id.insurer.currency_id', string="Company Currency", readonly=True,store=True)
    product_id = fields.Many2one('insurance.product')

    @api.constrains('datefrom')
    def _constrain_date(self):
        for record in self:
            if record.dateto < record.datefrom:
                raise ValidationError('Error! Date to Should be After Date from')


class inhertResPartner(models.Model):
    _inherit = 'res.partner'

    insurer_type=fields.Boolean('Insurer')
    insurer_branch=fields.Many2one("res.partner",string="Insurer Branch")
    holding_type=fields.Boolean("Holding",default=True)
    holding_company=fields.Many2one("res.partner",string="Holding Company")
    policy_count=fields.Integer(compute='_compute_policy_count')
    claim_count=fields.Integer(compute='_compute_claim_count')

    @api.multi
    def _compute_policy_count(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='
            partner.policy_count = self.env['policy.broker'].search_count(
                [('customer', operator, partner.id)])
    @api.multi
    def show_partner_policies(self):
        # form_view = self.env.ref('insurance_broker_blackbelts-master.my_view_for_policy_form_kmlo1')
        # if self.policy_number:testtest

        return {
            'name': ('Policy'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'policy.broker',#model name ?yes true ok
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_customer':self.id},
            'domain': [('customer','=',self.id)]
        }
    @api.multi
    def _compute_claim_count(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='
            partner.claim_count = self.env['insurance.claim'].search_count(
                [('customer_policy', operator, partner.id)])
    @api.multi
    def show_partner_claim(self):
        # form_view = self.env.ref('insurance_broker_blackbelts-master.my_view_for_policy_form_kmlo1')
        # if self.policy_number:testtest

        return {
            'name': ('Claim'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'insurance.claim',#model name ?yes true ok
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_customer_policy':self.id},
            'domain': [('customer_policy','=',self.id)]
        }

