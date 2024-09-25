# -*- coding:utf-8 -*-

#import logging

from odoo import fields, models, api

#logger = logging.getLogger(__name__)

class Presupuesto(models.Model):
    _name = 'presupuesto'
    _inherit = ['image.mixin']

    name = fields.Char(string='Pelicula', required=True)
    clasificacion = fields.Selection(selection=[
        ('G', 'G'),
        ('PG', 'PG'),
        ('PG-13', 'PG-13'),
        ('R', 'R'),
        ('NC-17', 'NC-17'),
    ], string='Clasificacion')    
    fch_estreno = fields.Date(string='Fecha de Estreno')
    puntuacion = fields.Integer(string='Puntuacion', related="puntuacion2")
    puntuacion2 = fields.Integer(string='Puntuacion2')
    
    #state = fields.Selection([
    #    ('draft', 'draft'),
    #    ('confirmed', 'confirmed'),
    #    ('readonly', 'readonly'),
    #], default='draft', string="Estado")

    active = fields.Boolean(
        string='Activo',
        default='True'
        )
    director_id = fields.Many2one(
        comodel_name='res.partner',
        string='Director'
    )
    categoria_director = fields.Many2one(
        comodel_name="res.partner.category",
        string="Categoria Director",
        default=lambda self: self.env['res.partner.category'].search([('name', '=', 'Director')])

    )
    genero_ids = fields.Many2many(
        comodel_name='genero',
        string='Genero'
    )
    vista_general = fields.Text(string='Descripcion')
    link_trailer = fields.Char(string='Trailer')
    es_libro = fields.Boolean(string='Version Libro')
    libro = fields.Binary(string='Libro')
    libro_filename = fields.Char(string='Nombre del libro')

    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('cancelado', 'Cancelado'),
    ], default='borrador', string='Estados', copy=False)

    fch_aprobado = fields.Datetime(string='Fecha aprobado', copy=False)

    def aprobar_presupuesto(self):
       #logger.info('Log info') 
       #logger.warning('Log warning') 
       #logger.error('Log error')
        self.state = 'aprobado'  
        self.fch_aprobado = fields.Datetime.now()   

    def cancelar_presupuesto(self):
        self.state = 'cancelado'

    def borrador_presupuesto(self):
        self.state = 'borrador'    