# -*- coding: utf-8 -*-
# from odoo import http


# class BenefitRequest(http.Controller):
#     @http.route('/benefit_request/benefit_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/benefit_request/benefit_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('benefit_request.listing', {
#             'root': '/benefit_request/benefit_request',
#             'objects': http.request.env['benefit_request.benefit_request'].search([]),
#         })

#     @http.route('/benefit_request/benefit_request/objects/<model("benefit_request.benefit_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('benefit_request.object', {
#             'object': obj
#         })
