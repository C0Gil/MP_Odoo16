# -*- coding:utf-8 -*-

{
    'name': 'Modulo de peliculas',
    'version': '1.0',
    'depends': [
      'contacts',

      ],
    'author': 'Gilberto C. O.',
    'category': 'Peliculas',
    'website': 'http://www.google.com',
    'summary': 'Modulo de presupuestos para peliculas',
    'description': '''
      Modulo para hacer presupuestos de peliculas
    ''',    
    'data': [
      'security/security.xml',
      'security/ir.model.access.csv',
      'data/secuencia.xml',
      'data/categoria.xml',
      'wizard/update_wizzard_views.xml',
      'views/presupuesto_view.xml',
      'views/menu.xml'
    ],
}