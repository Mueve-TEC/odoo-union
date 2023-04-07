# -*- coding: utf-8 -*-
# from odoo import http


# class SchoolPosition(http.Controller):
#     @http.route('/school_position/school_position/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/school_position/school_position/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('school_position.listing', {
#             'root': '/school_position/school_position',
#             'objects': http.request.env['school_position.school_position'].search([]),
#         })

#     @http.route('/school_position/school_position/objects/<model("school_position.school_position"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('school_position.object', {
#             'object': obj
#         })
