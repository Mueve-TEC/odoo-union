# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

log = logging.getLogger(__name__)


AFFILIATE_STR_TO_INT = {
    'active': 0,
    'retired': 1
}


class Affiliate(models.Model):
    _name = 'affiliation.affiliate'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Union affiliate entity'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        ondelete='cascade',
        required=True
    )
    uid = fields.Char(string='Affiliate UID', required=True)
    personal_id_type = fields.Selection([
        ('dni', 'DNI'),
        ('du', 'DU'),
        ('lc', 'LC'),
        ('le', 'LE'),
        ('pasaporte', 'PASAPORTE'),
        ('ci', 'CI')],
        string='Personal ID type', default='dni')
    personal_id = fields.Char(string='Personal ID')
    gender = fields.Selection([
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
        ('not_report', 'Not report')],
        string='Gender', default='not_report')
    civil_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('united', 'United'),
        ('separated', 'Separated'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('not_report', 'Not report')],
        string='Marital status', default='not_report')
    birth_date = fields.Date(string='Birth date')
    birth_country = fields.Many2one(
        comodel_name='res.country', string='Birth country')
    affiliate_child_ids = fields.Many2many(
        comodel_name='affiliation.affiliate_child',
        relation='affiliate_affiliate_child',
        column1='affiliate_id',
        column2='affiliate_child_id',
        string='Childs'
    )
    state = fields.Selection(
        selection=[
            ('not_affiliated', 'Not affiliated'),
            ('new', 'New'),
            ('pending_suscribe', 'Pending suscribe'),
            ('affiliated', 'Affiliated'),
            ('pending_unsuscribe', 'Pending unsuscribe'),
            ('disaffiliated', 'Disaffiliated'),
            ('historical', 'Historical'),
        ],
        string='Affiliate State',
        default='not_affiliated'
    )
    affiliation_period_ids = fields.One2many(
        comodel_name='affiliation.affiliation_period',
        inverse_name='affiliate_id',
        string='Affiliation periods'
    )
    affiliate_type_id = fields.Many2one(
        comodel_name='affiliation.affiliate_type',
        string='Employment relationship type',
        domain="[('enabled', '=', True)]",
        ondelete='restrict',
    )

    workplace_ids = fields.Many2many(
        comodel_name='union.workplace',
        relation='affiliate_workplace_rel',
        column1='affiliate_id',
        column2='workplace_id',
        string='Lugares de trabajo',
        help='Todos los lugares de trabajo del afiliado'
    )

    main_workplace_id = fields.Many2one(
        comodel_name='union.workplace',
        string='Lugar de trabajo principal',
        ondelete='set null',
        help='Lugar de trabajo principal para padrones (debe estar en la lista de lugares de trabajo)'
    )

    observations = fields.Text(string='Observations')
    quote = fields.Boolean(string='Contributor', default=False)
    log = fields.Text(string='Log')
    affiliation_number = fields.Integer(string='Affiliation number')
    affiliation_date = fields.Date(string='Affiliation\'s date')
    disaffiliation_date = fields.Date(string='Disaffiliation\'s date')
    seniority = fields.Date(string='Seniority')

    # EtiquetaBis
    category_bis_id = fields.Many2many(
        comodel_name='res.partner.category',
        relation='affiliate_category_bis_rel',
        column1='affiliate_id',
        column2='category_id',
        string='Etiqueta BIS'
    )

    @api.constrains('uid')
    def _check_uid(self):
        other = self.env['affiliation.affiliate'].search(
            [('uid', '=', self.uid)])
        if len(other.ids) > 1 or (len(other) == 1 and other[0].id != self.id):
            raise ValidationError(
                _('There is already exist an affiliate with the same uid!'))

    @api.constrains('affiliation_number')
    def _check_affiliation_number(self):
        if self.affiliation_number:
            other = self.env['affiliation.affiliate'].search(
                [('affiliation_number', '=', self.affiliation_number)])
            if len(other.ids) > 1 or (len(other) == 1 and other[0].id != self.id):
                raise ValidationError(
                    _("There is already exist an affiliated with the same affiliation number!"))

    @api.constrains('state', 'affiliate_type_id')
    def _check_affiliate_type_id(self):
        for record in self:
            if record.state not in ('new', 'not_affiliated') and not record.affiliate_type_id:
                raise ValidationError(
                    _("The field 'Employment relationship type' is required when state is not 'new' or 'not_affiliated'."))

    @api.constrains('main_workplace_id', 'workplace_ids')
    def _check_main_workplace(self):
        """Valida que el lugar de trabajo principal esté entre los lugares asignados"""
        # No validar durante eliminaciones de lugares de trabajo
        if self.env.context.get('from_delete_wizard') or self.env.context.get('skip_workplace_validation'):
            return

        for record in self:
            if record.main_workplace_id and record.main_workplace_id not in record.workplace_ids:
                raise ValidationError(_(
                    "El lugar de trabajo principal debe estar incluido en la lista de lugares de trabajo del afiliado."
                ))

    def _auto_assign_workplace_parents(self, workplace_ids):
        """Asigna automáticamente los lugares padres jerarquía"""
        if not workplace_ids:
            return workplace_ids

        all_workplaces = set(workplace_ids.ids if hasattr(
            workplace_ids, 'ids') else workplace_ids)
        workplaces_to_check = list(all_workplaces)

        for workplace_id in workplaces_to_check:
            workplace = self.env['union.workplace'].browse(workplace_id)
            parent = workplace.parent_id
            while parent:
                if parent.id not in all_workplaces:
                    all_workplaces.add(parent.id)
                parent = parent.parent_id

        return self.env['union.workplace'].browse(list(all_workplaces))

    # This method is necessary for RPC importation
    @api.model
    def create(self, vals):
        # Auto-asignar lugares de trabajo padres si se crean afiliados con workplace_ids
        if 'workplace_ids' in vals and not self.env.context.get('skip_workplace_validation'):
            res = super(Affiliate, self).create(vals)

            if res.workplace_ids:
                expanded_workplaces = res._auto_assign_workplace_parents(
                    res.workplace_ids.ids)
                res.workplace_ids = expanded_workplaces
            return res

        res = super(Affiliate, self).create(vals)
        return res

    def write(self, vals):
        self._log_change_field(vals)

        # Auto-asignar lugares padres si se modifican los workplace_ids
        if 'workplace_ids' in vals and not self.env.context.get('skip_workplace_validation'):
            res = super(Affiliate, self).write(vals)

            for record in self:
                if record.workplace_ids:
                    expanded_workplaces = record._auto_assign_workplace_parents(
                        record.workplace_ids.ids)
                    # Solo actualizar si hay cambios para evitar recursión
                    if set(expanded_workplaces.ids) != set(record.workplace_ids.ids):
                        record.with_context(
                            skip_workplace_validation=True).workplace_ids = expanded_workplaces
            return res

        res = super(Affiliate, self).write(vals)
        return res

    def unlink(self):
        self.partner_id.unlink()
        res = super(Affiliate, self).unlink()
        return res

    def action_affiliate(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'affiliation.affiliation_period',
            'views': [[False, 'form']],
            'target': 'new',
            'context': {
                'default_affiliate_id': self.id,
            }
        }

    def action_disaffiliate(self):
        return {
            'name': 'Period',
            'type': 'ir.actions.act_window',
            'res_model': 'affiliation.affiliation_period',
            'view_id': self.env.ref('affiliation.affiliation_affiliation_period_form').id,
            'view_mode': 'form',
            'res_id': self._get_current_period().id,
            'target': 'new',
        }

    def affiliate_(self):
        _config = self.env['affiliation.affiliation_configuration'].browse(1)
        _to_write = {'state': 'pending_suscribe'}
        if self.quote:
            _to_write.update({'quote': False})
        if _config.affiliation_start == 'on_affiliate':
            return self.start_affiliation_(_to_write, _config)
        else:
            self.write(_to_write)

    def confirm_affiliation_(self):
        _config = self.env['affiliation.affiliation_configuration'].browse(1)
        _to_write = {'state': 'affiliated'}
        if not self.quote:
            _to_write.update({'quote': True})

        if _config.affiliation_start == 'on_confirm':
            return self.start_affiliation_(_to_write, _config)
        else:
            self.write(_to_write)

    def start_affiliation_(self, _to_write, _config):

        _to_write.update({'affiliation_date': fields.Date.today()})

        suggested_affiliation_number = None
        if _config.enable_affiliation_number_sequence:
            suggested_affiliation_number = self.env['ir.sequence'].search(
                [('code', '=', 'next_affiliation_number_seq')], limit=1).number_next_actual
            if not suggested_affiliation_number:
                raise UserError(
                    _("The sequence next_affiliation_number_seq is not defined."))

        # TODO: find a way to delete the unconfirmed affiliations from database records
        _data = self.env['affiliation.affiliation_number'].create(
            {'affiliate_id': self.id,
             'affiliation_number': suggested_affiliation_number,
             'affiliation_number_edition': _config.affiliation_number_edition,
             'enable_affiliation_number_sequence': _config.enable_affiliation_number_sequence})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'affiliation.affiliation_number',
            'views': [[False, 'form']],
            'target': 'new',
            'res_id': _data.id,
            'context': _to_write
        }

    def disaffiliate_(self):
        _config = self.env['affiliation.affiliation_configuration'].browse(1)
        _to_write = {'state': 'pending_unsuscribe'}
        if _config.set_disaffiliation_date == 'on_disaffiliate':
            _to_write.update({'disaffiliation_date': fields.Date.today()})

        self.write(_to_write)

    def confirm_dissafiliation_(self):
        _config = self.env['affiliation.affiliation_configuration'].browse(1)
        _to_write = {'state': 'disaffiliated'}
        if _config.set_disaffiliation_date == 'on_confirm':
            _to_write.update({'disaffiliation_date': fields.Date.today()})
        if self.quote:
            _to_write.update({'quote': False})

        self.write(_to_write)

    def archive_(self):
        self.state = 'historical'
        if self.quote:
            self.set_contributor()

    def set_contributor(self):
        if not self.quote:
            self.write({'quote': True})
        else:
            self.write({'quote': False})

    def _get_current_period(self):
        _period = self.affiliation_period_ids.sorted(key='id', reverse=True)
        if len(_period) > 1:
            _period = _period[0]
        if not _period.closed:
            return _period
        return False

    def _log_change_field(self, vals):
        _loggables = ['state', 'quote', 'affiliate_type_id',
                      'email', 'phone', 'mobile', 'affiliation_number']
        for record in self:
            _log = ''
            for field in vals:
                if field in _loggables:
                    _log = _('%s [%s] The field %s change from %s to %s \n') % (str(fields.Date.today(
                    )), record.env.user.name, _(field), _(record[field]), _(str(vals[field]))) + _log
            _log = _log + record.log if record.log else _log
            vals.update({'log': _log})

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            domain = ['|', '|',
                      ('personal_id', operator, name),
                      ('uid', operator, name),
                      ('name', operator, name)]
            # Buscar directamente con el dominio personalizado
            return self._search(args + domain, limit=limit)
        return super()._name_search(name, args, operator, limit)

    def _message_get_suggested_recipients(self):
        recipients = super(Affiliate, self)._message_get_suggested_recipients()
        recipients[self.id].append((self.partner_id.id, self.name, 'Afiliado'))
        return recipients

    def action_archive(self):
        log.info(self.env.user.groups_id)
        if not self.env.user.has_group('affiliation.group_affiliation_admin'):
            raise UserError(
                _("Admin affiliation permission is required to archive records."))
        return super().action_archive()

    def action_unarchive(self):
        if not self.env.user.has_group('affiliation.group_affiliation_admin'):
            raise UserError(
                _("Admin affiliation permission is required to unarchive records."))
        return super().action_unarchive()
