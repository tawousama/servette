odoo.define('custom_base.settings', function (require) {
"use strict";

var BaseSettingRenderer = require('base.settings').Renderer;

BaseSettingRenderer.include({

    _getAppIconUrl: function (module) {
        if (module == 'prestashop_connector_gt_websites' || module == 'prestashop_connector_gt_storeviews') {
            return "/prestashop_connector_gt/static/description/Banner.gif";
        }
        else {
            return this._super.apply(this, arguments);
        }
    }
});
})