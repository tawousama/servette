
{
    'name': 'Servette Music - Import Zip codes',
    'version': '12.0.1.0.0',
    'author': 'Openfuture',

    'website': 'https://openfuture.ch/',
    'category': 'Localisation',

    'summary': 'Provides all Swiss postal codes for auto-completion',
    'depends': [
        'base',
        'base_location',
    ],
    'data': [
        'views/res_city_zip_views.xml',
    ],
    'application': True,
}
