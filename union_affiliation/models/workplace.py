# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class UnionWorkplace(models.Model):
    _name = 'union.workplace'
    _description = 'Lugar de trabajo'
    _order = 'complete_name'
    _parent_store = True
    _rec_name = 'complete_name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre del lugar de trabajo'
    )

    code = fields.Char(
        string='Código',
        required=True,
        help='Código único del lugar de trabajo'
    )

    parent_id = fields.Many2one(
        'union.workplace',
        string='Dependencia superior',
        index=True,
        ondelete='cascade',
        help='Lugar de trabajo padre en la jerarquía'
    )

    level = fields.Integer(
        string='Nivel',
        compute='_compute_level',
        store=True
    )

    child_ids = fields.One2many(
        'union.workplace',
        'parent_id',
        string='Dependencias inferiores'
    )

    # campo de odoo para jerarquías
    parent_path = fields.Char(index=True)

    complete_name = fields.Char(
        string='Nombre completo',
        compute='_compute_complete_name',
        recursive=True,
        store=True
    )

    active = fields.Boolean(
        string='Activo',
        default=True
    )

    # Relación con afiliados
    affiliate_ids = fields.Many2many(
        'affiliation.affiliate',
        relation='affiliate_workplace_rel',
        column1='workplace_id',
        column2='affiliate_id',
        string='Afiliados'
    )

    main_affiliate_ids = fields.One2many(
        'affiliation.affiliate',
        'main_workplace_id',
        string='Afiliados principales',
        help='Afiliados que tienen este lugar como principal'
    )

    # Campos estadísticos
    affiliate_count = fields.Integer(
        string='Cantidad de afiliados',
        compute='_compute_affiliate_count'
    )

    main_affiliate_count = fields.Integer(
        string='Afiliados pincipales',
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
        """Evita ciclos en la jerarquía"""
        if not self._check_recursion():
            raise ValidationError(
                'No puede crear una jerarquía recursiva de lugares de trabajo.')

    @api.constrains('name')
    def _check_unique_name(self):
        """El nombre debe ser único"""
        for workplace in self:
            if workplace.name:
                existing = self.search([
                    ('name', '=', workplace.name),
                    ('id', '!=', workplace.id)
                ])
                if existing:
                    raise ValidationError(
                        f'El nombre "{workplace.name}" ya existe en otro lugar de trabajo.')

    @api.constrains('code')
    def _check_unique_code(self):
        """El código debe ser único"""
        for workplace in self:
            if workplace.code:
                existing = self.search([
                    ('code', '=', workplace.code),
                    ('id', '!=', workplace.id)
                ])
                if existing:
                    raise ValidationError(
                        f'El código "{workplace.code}" ya existe en otro lugar de trabajo.')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Permite buscar por código o nombre"""
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
        Método para obtener afiliados principales para padrones.
        Evita duplicados usando solo el lugar de trabajo principal.
        """
        return self.main_affiliate_ids.filtered(lambda a: a.state == 'affiliated')

    def _get_all_descendants(self):
        """
        Obtiene todos los descendientes (hijos, nietos, etc.) de forma recursiva.
        Retorna un recordset con todos los descendientes.
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
        Acción personalizada para eliminar con el wizard de confirmación
        """
        if len(self) != 1:
            raise UserError(
                "Por favor, seleccione un solo lugar de trabajo para eliminar.")

        workplace = self[0]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirmar eliminación',
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
        Override del método unlink para limpiar correctamente las relaciones Many2many
        antes de eliminar el lugar de trabajo.
        """
        # Obtener todos los lugares que van a ser eliminados (incluyendo descendientes)
        all_workplaces_to_delete = self.env['union.workplace']

        for workplace in self:
            all_workplaces_to_delete |= workplace
            all_workplaces_to_delete |= workplace._get_all_descendants()

        # Limpiar las relaciones Many2many con los afiliados para todos los lugares que se eliminarán
        if all_workplaces_to_delete and self.env.context.get('from_delete_wizard'):
            affected_affiliates = self.env['affiliation.affiliate'].search([
                ('workplace_ids', 'in', all_workplaces_to_delete.ids)
            ])

            # Remover estos lugares de trabajo de los afiliados con contexto especial
            ctx = dict(self.env.context, skip_workplace_validation=True)
            for affiliate in affected_affiliates:
                affiliate.with_context(
                    ctx).workplace_ids = affiliate.workplace_ids - all_workplaces_to_delete

                # Si el lugar principal está siendo eliminado, verificar que tenga otro lugar principal válido
                if affiliate.main_workplace_id and affiliate.main_workplace_id in all_workplaces_to_delete:
                    # Si aún tiene otros lugares de trabajo, sugerir el primero como principal
                    if affiliate.workplace_ids:
                        affiliate.with_context(
                            ctx).main_workplace_id = affiliate.workplace_ids[0]
                    # Si no tiene otros lugares, main_workplace_id se pondrá en NULL automáticamente por ondelete='set null'

        # Continuar con la eliminación normal
        return super().unlink()

    @api.ondelete(at_uninstall=False)
    def _checks_before_delete(self):

        # Permitir eliminación desde el wizard
        if self.env.context.get('from_delete_wizard'):
            return

        # Para eliminaciones desde interfaz, redirigir al wizard si hay hijos o afiliados asociados al lugar de trabajo
        for workplace in self:
            all_descendants = workplace._get_all_descendants()
            if all_descendants:
                raise ValidationError(_(
                    'Para eliminar este lugar de trabajo y sus descendientes, '
                    'Use el botón "Eliminar" desde la vista formulario.'
                ))

            if workplace.affiliate_ids:
                raise ValidationError(_(
                    'No se puede eliminar este lugar de trabajo porque tiene afiliados asociados. '
                    'Use el botón "Eliminar" desde la vista formulario.'
                ))
