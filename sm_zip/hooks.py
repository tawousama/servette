
from odoo.tools import convert_file


def import_csv_data(cr, registry):

    filenames = ['data/res.city.csv','data/data2/res.city.csv', 'data/res.city.zip.csv']
    for filename in filenames:
        convert_file(
            cr, 'sm_zip',
            filename, None, mode='init', noupdate=True,
            kind='init',
        )
        print("Import_csv_data", filename)


def post_init(cr, registry):
    import_csv_data(cr, registry)
