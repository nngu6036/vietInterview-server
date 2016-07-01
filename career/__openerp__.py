# -*- coding: utf-8 -*-
{
    'name': "Career",

    'summary': """
		Human Resource Recruitment Module
        """,

    'description': """
        Human Resource Recruitment Module
    """,

    'author': "Quang Nguyen",
    'website': "http://www.vietinterview.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr,recruitment',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','survey','hr_recruitment','email_template','mass_mailing','hr_evaluation'],

    # always loaded
    'data': [
        'data/data.xml',
        'data/assessment.xml',
        'data/question_bank.xml',
        'data/job.xml',
        'data/install.xml',
        'data/mail.xml',
        'data/location.xml',
         'security/ir.model.access.csv'

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
