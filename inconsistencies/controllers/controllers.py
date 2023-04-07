# -*- coding: utf-8 -*-
# from odoo import http


# class Inconsistencies(http.Controller):
#     @http.route('/inconsistencies/inconsistencies/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inconsistencies/inconsistencies/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inconsistencies.listing', {
#             'root': '/inconsistencies/inconsistencies',
#             'objects': http.request.env['inconsistencies.inconsistencies'].search([]),
#         })

#     @http.route('/inconsistencies/inconsistencies/objects/<model("inconsistencies.inconsistencies"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inconsistencies.object', {
#             'object': obj
#         })
