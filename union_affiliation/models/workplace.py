# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class UnionWorkplace(models.Model):
    _name = 'union.workplace'
    _description = 'Workplace'
    _order = 'complete_name'
    _parent_store = True
    _rec_name = 'complete_name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Workplace name'
    )

    code = fields.Char(
        string='Code',
        required=True,
        help='Unique workplace code'
    )

    parent_id = fields.Many2one(
        'union.workplace',
        string='Parent Workplace',
        index=True,
        ondelete='cascade',
        help='Parent workplace in the hierarchy'
    )

    level = fields.Integer(
        string='Level',
        compute='_compute_level',
        store=True
    )

    child_ids = fields.One2many(
        'union.workplace',
        'parent_id',
        string='Child Workplaces'
    )

    # Odoo field for hierarchies
    parent_path = fields.Char(index=True)

    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Relationship with affiliates
    affiliate_ids = fields.Many2many(
        'affiliation.affiliate',
        relation='affiliate_workplace_rel',
        column1='workplace_id',
        column2='affiliate_id',
        string='Affiliates'
    )

    main_affiliate_ids = fields.One2many(
        'affiliation.affiliate',
        'main_workplace_id',
        string='Main Affiliates',
        help='Affiliates that have this workplace as main'
    )

    # Statistical fields
    affiliate_count = fields.Integer(
        string='Affiliate Count',
        compute='_compute_affiliate_count'
    )

    main_affiliate_count = fields.Integer(
        string='Main Affiliate Count',
        compute='_compute_main_affiliate_count'
    )

    @api.depends('parent_id')
    def _compute_level(self):
        for workplace in self:
            if workplace.parent_id:
                workplace.level = workplace.parent_id.level + 1
            else:
                workplace.level = 1

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for workplace in self:
            if workplace.parent_id:
                workplace.complete_name = f"{workplace.parent_id.complete_name} / {workplace.name}"
            else:
                workplace.complete_name = workplace.name

    @api.depends('affiliate_ids')
    def _compute_affiliate_count(self):
        for workplace in self:
            workplace.affiliate_count = len(workplace.affiliate_ids)

    @api.depends('main_affiliate_ids')
    def _compute_main_affiliate_count(self):
        for workplace in self:
            workplace.main_affiliate_count = len(workplace.main_affiliate_ids)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Prevents cycles in the hierarchy"""
        if not self._check_recursion():
            raise ValidationError(
                _('You cannot create a recursive workplace hierarchy.'))

    @api.constrains('name')
    def _check_unique_name(self):
        """Name must be unique"""
        for workplace in self:
            if workplace.name:
                existing = self.search([
                    ('name', '=', workplace.name),
                    ('id', '!=', workplace.id)
                ])
                if existing:
                    raise ValidationError(
                        _('The name "%s" already exists in another workplace.') % workplace.name)

    @api.constrains('code')
    def _check_unique_code(self):
        """Code must be unique"""
        for workplace in self:
            if workplace.code:
                existing = self.search([
                    ('code', '=', workplace.code),
                    ('id', '!=', workplace.id)
                ])
                if existing:
                    raise ValidationError(
                        _('The code "%s" already exists in another workplace.') % workplace.code)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Allows searching by code or name"""
        args = args or []
        domain = []
        if name:
            domain = [
                '|', '|',
                ('name', operator, name),
                ('code', operator, name),
                ('complete_name', operator, name)
            ]
        workplaces = self.search(domain + args, limit=limit)
        return workplaces.name_get()

    def get_main_affiliates_for_reports(self):
        """
        Method to get main affiliates for reports.
        Avoids duplicates by using only the main workplace.
        """
        return self.main_affiliate_ids.filtered(lambda a: a.state == 'affiliated')

    def _get_all_descendants(self):
        """
        Gets all descendants (children, grandchildren, etc.) recursively.
        Returns a recordset with all descendants.
        """
        descendants = self.env['union.workplace']

        if not self.child_ids:
            return descendants

        descendants |= self.child_ids
        for child in self.child_ids:
            descendants |= child._get_all_descendants()

        return descendants

    def action_delete_with_confirmation(self):
        """
        Custom action to delete with confirmation wizard
        """
        if len(self) != 1:
            raise UserError(
                _("Please select only one workplace to delete."))

        workplace = self[0]

        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirm Deletion'),
            'res_model': 'union.workplace.delete.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'workplace_id': workplace.id,
                'from_delete_wizard': True,
            }
        }

    def unlink(self):
        """
        Override the unlink method to properly clean Many2many relationships
        before deleting the workplace.
        """
        # Get all workplaces that will be deleted (including descendants)
        all_workplaces_to_delete = self.env['union.workplace']

        for workplace in self:
            all_workplaces_to_delete |= workplace
            all_workplaces_to_delete |= workplace._get_all_descendants()

        # Clean Many2many relationships with affiliates for all workplaces to be deleted
        if all_workplaces_to_delete and self.env.context.get('from_delete_wizard'):
            affected_affiliates = self.env['affiliation.affiliate'].search([
                ('workplace_ids', 'in', all_workplaces_to_delete.ids)
            ])

            # Remove these workplaces from affiliates with special context
            ctx = dict(self.env.context, skip_workplace_validation=True)
            for affiliate in affected_affiliates:
                affiliate.with_context(
                    ctx).workplace_ids = affiliate.workplace_ids - all_workplaces_to_delete

                # If main workplace is being deleted, verify it has another valid main workplace
                if affiliate.main_workplace_id and affiliate.main_workplace_id in all_workplaces_to_delete:
                    # If it still has other workplaces, suggest the first one as main
                    if affiliate.workplace_ids:
                        affiliate.with_context(
                            ctx).main_workplace_id = affiliate.workplace_ids[0]
                    # If it has no other workplaces, main_workplace_id will be set to NULL automatically by ondelete='set null'

        # Continue with normal deletion
        return super().unlink()

    @api.ondelete(at_uninstall=False)
    def _checks_before_delete(self):

        # Allow deletion from wizard
        if self.env.context.get('from_delete_wizard'):
            return

        # For deletions from interface, redirect to wizard if there are children or affiliates associated with the workplace
        for workplace in self:
            all_descendants = workplace._get_all_descendants()
            if all_descendants:
                raise ValidationError(_(
                    'To delete this workplace and its descendants, '
                    'use the "Delete" button from the form view.'
                ))

            if workplace.affiliate_ids:
                raise ValidationError(_(
                    'Cannot delete this workplace because it has associated affiliates. '
                    'Use the "Delete" button from the form view.'
                ))
