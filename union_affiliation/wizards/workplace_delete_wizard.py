# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class UnionWorkplaceDeleteWizard(models.TransientModel):
    _name = 'union.workplace.delete.wizard'
    _description = 'Wizard para confirmar eliminación de lugar de trabajo'

    workplace_id = fields.Many2one(
        'union.workplace',
        string='Lugar de trabajo',
        required=True
    )

    message = fields.Text(
        string='Mensaje de confirmación',
        readonly=True
    )

    def action_confirm_delete(self):
        """
        Confirma y ejecuta la eliminación, luego redirije a la vista tree
        """
        if self.workplace_id:
            # Usar contexto especial para permitir eliminación
            self.workplace_id.with_context(from_delete_wizard=True).unlink()

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

    def action_cancel(self):
        """
        Cancela la eliminación
        """
        return {'type': 'ir.actions.act_window_close'}
