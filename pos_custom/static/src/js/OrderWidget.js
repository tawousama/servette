odoo.define('pos_custom.OrderWidget', function (require) {
    'use strict';

    const OrderWidget = require('point_of_sale.OrderWidget');
    const Registries = require('point_of_sale.Registries');

    const NewOrderWidget = (OrderWidget) =>
        class extends OrderWidget {
            captureChange(ev) {
                this.order.note = $(ev.currentTarget).val()
            }
        };

    Registries.Component.extend(OrderWidget, NewOrderWidget);

    return  OrderWidget;

});