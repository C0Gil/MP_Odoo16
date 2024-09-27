# -*- coding:utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

class Presupuesto(models.Model):
    _name = 'presupuesto'
    _inherit = ['mail.thread', 'mail.activity.mixin','image.mixin']

    @api.depends('detalle_ids')
    def _compute_total(self):
        for record in self:
            sub_total = 0
            for linea in record.detalle_ids:
                sub_total += linea.importe
            record.base = sub_total
            record.impuestos = sub_total * 0.16
            record.total = sub_total * 1.16

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
        #Segunda version
        default=lambda self: self.env.ref('peliculas.category_director')

        #Primera version
        #default=lambda self: self.env['res.partner.category'].search([('name', '=', 'Director')])
    )
    actor_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Actores"
    )
    categoria_actor = fields.Many2one(
        comodel_name="res.partner.category",
        string="Categoria Actor",
        default=lambda self: self.env.ref('peliculas.category_actor')
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
    num_presupuesto = fields.Char(string='Numero presupuesto', copy=False)
    fch_creacion = fields.Datetime(string='Fecha de creacion', copy=False, default=lambda self: fields.Datetime.now())
    opinion = fields.Html(string='Opinion')

    detalle_ids = fields.One2many(
        comodel_name = 'presupuesto.detalle',
        inverse_name = 'presupuesto_id',
        string = 'Detalles'
    )
    campos_ocultos = fields.Boolean(string="Campos Ocultos", default='False')
    currency_id = fields.Many2one(
        comodel_name ="res.currency",
        string = 'Moneda',
        default=lambda self: self.env.company.currency_id.id
    )

    terminos = fields.Text(string='terminos')
    base = fields.Monetary(string='Total sin impuestos', compute='_compute_total')
    impuestos = fields.Monetary(string='Impuestos', compute='_compute_total')
    total = fields.Monetary(string='Total', compute='_compute_total')

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
        for record in self:
            if record.state != 'cancelado':
                raise UserError('Un registro necesita estar cancelado para ser eliminado')
            super(Presupuesto, record).unlink()

    @api.model
    def create(self, variables):
        logger.info('+----------------Variable: {0}'.format(variables))
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.presupuesto.pelicula')
        variables['num_presupuesto'] = correlativo
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

class PresupuestoDetalle(models.Model):
    _name = "presupuesto.detalle"
    
    def _compute_is_guide(self):
        # Obtener el grupo del usuario actual
        usuario = self.env.user
        grupo_ref = 'peliculas.group_pelicula_administrador'
        es_usuario_del_grupo = usuario.has_group(grupo_ref)
        for record in self:
            record.is_guide = es_usuario_del_grupo
    
    is_guide = fields.Boolean(compute='_compute_is_guide', store=False, string='Tipo de Usuario')

    presupuesto_id = fields.Many2one(
        comodel_name = 'presupuesto',
        string = 'Presupuesto'
    )

    name = fields.Many2one(
        comodel_name='recurso.cinematografico',
        string="Recurso",
    )

    descripcion = fields.Char(string="Descripcion", related='name.descripcion')

    contacto_id = fields.Many2one(
        comodel_name="res.partner",
        string='Contacto',
        related='name.contacto_id',
    )

    image = fields.Binary(string='Imagen', related='name.image')
    cantidad = fields.Float(string='Cantidad', default=1.0, digit=(16,4))
    precio = fields.Float(string='Precio', digits='Product Price')
    importe = fields.Monetary(string='Importe')

    currency_id = fields.Many2one(
        comodel_name = 'res.currency',
        string = 'Moneda',
        related= 'presupuesto_id.currency_id'
    )

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.precio = self.name.precio
    
    @api.onchange('cantidad', 'precio')
    def _onchange_importe(self):
        self.importe = self.cantidad * self.precio