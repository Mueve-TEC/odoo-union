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
        string='Lugar Padre',
        index=True,
        ondelete='cascade',
        help='Lugar de trabajo padre en la jerarquía'
    )

    child_ids = fields.One2many(
        'union.workplace',
        'parent_id',
        string='Lugares Hijos'
    )

    # campo de odoo para jerarquías
    parent_path = fields.Char(index=True)

    complete_name = fields.Char(
        string='Nombre Completo',
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
        string='Afiliados Principales',
        help='Afiliados que tienen este lugar como principal'
    )

    # Campos estadísticos
    affiliate_count = fields.Integer(
        string='Cantidad de Afiliados',
        compute='_compute_affiliate_count'
    )

    main_affiliate_count = fields.Integer(
        string='Afiliados Principales',
        compute='_compute_main_affiliate_count'
    )

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

    def name_get(self):
        """Personaliza cómo se muestra el nombre en selecciones"""
        result = []
        for workplace in self:
            name = workplace.complete_name
            if workplace.code:
                name = f"[{workplace.code}] {name}"
            result.append((workplace.id, name))
        return result

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

        # Si no tiene hijos, retornar vacío
        if not self.child_ids:
            return descendants

        # Agregar los hijos directos
        descendants |= self.child_ids

        # Agregar recursivamente los descendientes de cada hijo
        for child in self.child_ids:
            descendants |= child._get_all_descendants()

        return descendants

    def action_delete_with_confirmation(self):
        """
        Acción personalizada para eliminar con confirmación detallada
        """
        for workplace in self:
            all_descendants = workplace._get_all_descendants()

            if all_descendants:
                # Construir mensaje detallado
                sorted_descendants = all_descendants.sorted(
                    lambda x: x.parent_path or '')
                descendant_names = sorted_descendants.mapped('complete_name')
                total_count = len(descendant_names)

                if total_count == 1:
                    title = "Confirmar eliminación"
                    message = f'Al eliminar "{workplace.complete_name}", también se eliminará 1 lugar descendiente:\n\n• {descendant_names[0]}'
                else:
                    display_limit = 10
                    descendant_list = '\n• '.join(
                        descendant_names[:display_limit])
                    if total_count > display_limit:
                        descendant_list += f'\n... y {total_count - display_limit} más'

                    title = "Confirmar eliminación"
                    message = f'Al eliminar "{workplace.complete_name}", también se eliminarán {total_count} lugares descendientes:\n\n• {descendant_list}'

                # Mostrar wizard de confirmación
                return {
                    'type': 'ir.actions.act_window',
                    'name': title,
                    'res_model': 'union.workplace.delete.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_workplace_id': workplace.id,
                        'default_message': message,
                    }
                }
            else:
                # Si no tiene descendientes, eliminar directamente y redireccionar
                workplace.unlink()

                # Redirigir usando la acción del menú
                action_ref = self.env.ref(
                    'union_affiliation.union_workplace_list_action')
                action = action_ref.read()[0] if action_ref else {}

                action.update({
                    'target': 'main',
                    'context': {
                        'search_default_filter_active': 1,
                    },
                    'flags': {'clear_breadcrumbs': True}
                })

                return action

    @api.ondelete(at_uninstall=False)
    def _check_child_workplaces_before_delete(self):
        """
        Solo impide eliminación si se llama desde código.
        La eliminación manual debe usar action_delete_with_confirmation.
        """
        # Solo validar si es una eliminación programática (no desde interfaz)
        if self.env.context.get('from_delete_wizard'):
            # Permitir eliminación desde el wizard
            return

        # Para eliminaciones desde interfaz, redirigir al wizard
        for workplace in self:
            all_descendants = workplace._get_all_descendants()
            if all_descendants:
                raise ValidationError(_(
                    'Para eliminar este lugar de trabajo y sus descendientes, '
                    'use el botón "Eliminar con confirmación" desde el formulario.'
                ))
