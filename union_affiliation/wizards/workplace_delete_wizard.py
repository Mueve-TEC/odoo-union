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

    affected_affiliates = fields.Text(
        string='Afiliados afectados',
        readonly=True
    )

    @api.model
    def default_get(self, fields):
        """
        Preparar información detallada sobre la eliminación
        """
        res = super().default_get(fields)
        if 'workplace_id' in self._context:
            workplace_id = self._context['workplace_id']
            workplace = self.env['union.workplace'].browse(workplace_id)

            if workplace:
                res['workplace_id'] = workplace_id

                # Obtener todos los descendientes
                descendants = workplace._get_all_descendants()
                all_workplaces = workplace | descendants

                # Obtener afiliados que usan estos lugares como principal
                main_affiliates = self.env['affiliation.affiliate'].search([
                    ('main_workplace_id', 'in', all_workplaces.ids)
                ])

                # Obtener afiliados asociados a estos lugares
                related_affiliates = self.env['affiliation.affiliate'].search([
                    ('workplace_ids', 'in', all_workplaces.ids)
                ])

                # Construir mensaje
                message_parts = []
                if descendants:
                    descendant_count = len(descendants)
                    # Mostrar detalles de lugares descendientes
                    sorted_descendants = descendants.sorted(
                        lambda x: x.parent_path or '')
                    descendant_names = sorted_descendants.mapped(
                        'complete_name')

                    if descendant_count == 1:
                        message_parts.append(
                            f"• Se eliminará 1 lugar de trabajo dependiente: {descendant_names[0]}")
                    else:
                        display_limit = 5
                        descendant_list = '\n  - '.join(
                            descendant_names[:display_limit])
                        if descendant_count > display_limit:
                            descendant_list += f'\n  - ... y {descendant_count - display_limit} más'

                        message_parts.append(
                            f"• Se eliminarán {descendant_count} lugares de trabajo dependientes:\n  - {descendant_list}")

                if main_affiliates:
                    main_count = len(main_affiliates)
                    message_parts.append(
                        f"• {main_count} afiliados perderán su lugar de trabajo principal")

                if related_affiliates:
                    related_count = len(related_affiliates)
                    message_parts.append(
                        f"• {related_count} afiliados serán desvinculados de estos lugares")

                if message_parts:
                    res['message'] = "Esta eliminación tendrá los siguientes efectos:\n\n" + \
                        "\n".join(message_parts)

                    # Detalles de afiliados afectados
                    if main_affiliates:
                        affiliate_details = []
                        # Mostrar solo los primeros 10
                        for affiliate in main_affiliates[:10]:
                            affiliate_details.append(
                                f"• {affiliate.name} ({affiliate.uid})")

                        if len(main_affiliates) > 10:
                            affiliate_details.append(
                                f"... y {len(main_affiliates) - 10} más")

                        res['affected_affiliates'] = "Afiliados que perderán su lugar principal:\n\n" + \
                            "\n".join(affiliate_details)
                else:
                    res['message'] = "¿Está seguro que desea eliminar este lugar de trabajo?\n\nNo hay afiliados asociados."

        return res

    def action_confirm_delete(self):
        """
        Confirma y ejecuta la eliminación, luego redirije a la vista tree
        """
        if self.workplace_id:
            # Usar contexto especial para permitir eliminación y pasar a las validaciones de afiliados
            ctx = dict(self.env.context, from_delete_wizard=True,
                       skip_workplace_validation=True)
            self.workplace_id.with_context(ctx).unlink()

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
