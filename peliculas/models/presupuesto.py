# -*- coding:utf-8 -*-

from odoo import fields, models, api

class Presupuesto(models.Model):
    _name = 'presupuesto'

    name = fields.Char()
