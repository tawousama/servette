odoo.define('pos_custom.models', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

//odoo.define('pos_custom.models', function (require) {

//    var models = require('point_of_sale.models');

//
//    models.load_fields('res.partner', ['category_id', 'mobile', 'firstname', 'lastname', 'zip_id', 'type']);
const NewPosGlobalState = (PosGlobalState) => class NewPosGlobalState extends PosGlobalState {
   async _processData(loadedData) {
  	 await super._processData(...arguments);
  	 this.zips = loadedData['res.city.zip'];
  	 this.tags = loadedData['res.partner.category'];
  	 }
}
Registries.Model.extend(PosGlobalState, NewPosGlobalState);

//
//    models.load_models([
//        {
//            model: 'res.partner.category',
//            label: 'load_tags',
//            fields: ['name', 'display_name', 'color'],
//            loaded: function (self, tags) {
//                self.tags = tags;
//
//            },
//        },
//        {
//            model:  'res.city.zip',
//            label: 'load_zips',
//            fields: ['name', 'city_id', 'state_id','country_id', 'display_name'],
//            loaded: function(self,zips){
//                self.zips = zips;
//            },
//        },
//
//    ])
//    var _super = models.Order.prototype;
//    models.Order = models.Order.extend({
//
//        export_as_JSON: function () {
//            var json = _super.export_as_JSON.apply(this, arguments);
//            json.note = this.note;
//            return json;
//        },
//        export_for_printing: function () {
//            var result = _super.export_for_printing.apply(this, arguments);
//            result.note = this.note;
//            return result;
//    },
//
//    });

});
