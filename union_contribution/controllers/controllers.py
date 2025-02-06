# -*- coding: utf-8 -*-
# from odoo import http


# class Contribution(http.Controller):
#     @http.route('/contribution/contribution/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contribution/contribution/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contribution.listing', {
#             'root': '/contribution/contribution',
#             'objects': http.request.env['contribution.contribution'].search([]),
#         })

#     @http.route('/contribution/contribution/objects/<model("contribution.contribution"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contribution.object', {
#             'object': obj
#         })
