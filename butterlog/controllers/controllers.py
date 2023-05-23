# -*- coding: utf-8 -*-
# from odoo import http


# class Butter-log(http.Controller):
#     @http.route('/butter-log/butter-log/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/butter-log/butter-log/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('butter-log.listing', {
#             'root': '/butter-log/butter-log',
#             'objects': http.request.env['butter-log.butter-log'].search([]),
#         })

#     @http.route('/butter-log/butter-log/objects/<model("butter-log.butter-log"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('butter-log.object', {
#             'object': obj
#         })
