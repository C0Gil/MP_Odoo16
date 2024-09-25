# -*- coding:utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

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
    dsc_clasificacion = fields.Char("Descripcion clasificacion")
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
        logger.info('+----------------Log info----------------+')       
        self.state = 'aprobado'  
        self.fch_aprobado = fields.Datetime.now()   

    def cancelar_presupuesto(self):
        self.state = 'cancelado'

    def borrador_presupuesto(self):
        self.state = 'borrador'    

    def unlink(self):
        logger.info('+----------------Se disparo la funcion unlink----------------+')
        if self.state != 'cancelado':
            raise UserError('Un registro necesita estar cancelado para ser eliminado')
        super(Presupuesto, self).unlink()

    @api.model
    def create(self, variables):
        logger.info('+----------------Variable: {0}'.format(variables))
        return super(Presupuesto, self).create(variables)
        
    def write(self, variables):
        logger.info('+----------------Variable: {0}'.format(variables))
        if 'clasificacion' in variables:
            raise UserError('La clasificacion no se puede editar')
        return super(Presupuesto, self).write(variables)

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.name + '(copia)'
        default['puntuacion2'] = 0
        return super(Presupuesto, self).copy(default)

    @api.onchange('clasificacion')
    def _onchange_clasificacion(self):
        if self.clasificacion:
            if self.clasificacion == 'G':
                self.dsc_clasificacion = 'Publico general'
            if self.clasificacion == 'PG':
                self.dsc_clasificacion = 'Se recomineda la compania de un adulto'
            if self.clasificacion == 'PG-13':
                self.dsc_clasificacion = 'Mayores de 13'
            if self.clasificacion == 'R':
                self.dsc_clasificacion = 'En compania de un adulto obligatorio'
            if self.clasificacion == 'NC-17':
                self.dsc_clasificacion = 'Mayores de 18'
        else:
            self.dsc_clasificacion = False
            
        
