odoo.define('pricelist_report_servette_music.generate_pricelist_sm', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var FieldMany2One = require('web.relational_fields').FieldMany2One;
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var GeneratePriceListSM = AbstractAction.extend(StandaloneFieldManagerMixin, {
    hasControlPanel: true,
    events: {
        'click .o_action': '_onClickAction',
        'submit form': '_onSubmitForm',
    },
    custom_events: Object.assign({}, StandaloneFieldManagerMixin.custom_events, {
        field_changed: '_onFieldChanged',
    }),
    /**
     * @override
     */
    init: function (parent, params) {
        this._super.apply(this, arguments);

        StandaloneFieldManagerMixin.init.call(this);
        this.context = params.context;
        // in case the window got refreshed
        if (params.params && params.params.active_ids && typeof(params.params.active_ids === 'string')) {
            try {
                this.context.active_ids = params.params.active_ids.split(',').map(id => parseInt(id));
                this.context.active_model = params.params.active_model;
            } catch(e) {
                console.log('unable to load ids from the url fragment 🙁');
            }
        }
        if (!this.context.active_model) {
            // started without an active module, assume product templates
            this.context.active_model = 'product.template';
        }
        this.context.quantities = [1];
        if (!this.context.with_ref)
        {
        this.context.with_ref=Boolean(false);
        }
        if (params.params && params.params.with_ref) {
           this.context.with_ref = Boolean(params.params.with_ref);


        }

    },
    /**
     * @override
     */
    willStart: function () {
        let getPricelit;
        // started without a selected pricelist in context? just get the first one

        if (this.context.default_pricelist) {
            getPricelit = Promise.resolve([this.context.default_pricelist]);
        } else {
            getPricelit = this._rpc({
                model: 'product.pricelist',
                method: 'search',
                args: [[]],
                kwargs: {limit: 1}
            })
        }
        const fieldSetup = getPricelit.then(pricelistIds => {
            return this.model.makeRecord('report.pricelist_report_servette_music.report_pricelist', [{
                name: 'pricelist_id',
                type: 'many2one',
                relation: 'product.pricelist',
                value: pricelistIds[0],
            }]);
        }).then(recordID => {
            const record = this.model.get(recordID);
            this.many2one = new FieldMany2One(this, 'pricelist_id', record, {
                mode: 'edit',
                attrs: {
                    can_create: false,
                    can_write: true,
                    options: {no_open: false},

                },
            });
            this._registerWidget(recordID, 'pricelist_id', this.many2one);
        });
        return Promise.all([fieldSetup, this._getHtml(), this._super()]);
    },
    /**
     * @override
     */
    start: function () {
        this.controlPanelProps.cp_content = this._renderComponent();
        return this._super.apply(this, arguments).then(() => {
            this.$('.o_content').html(this.reportHtml);
        });
    },

    getState: function() {
        return {
            active_model: this.context.active_model,
            with_ref: Boolean(this.context.with_ref),
        };
    },
    getTitle: function() {
        return _t('Rapport liste de prix Servette Music');
    },


    _getHtml: function () {
        return this._rpc({
            model: 'report.pricelist_report_servette_music.report_pricelist',
            method: 'get_html',
            kwargs: {context: this.context},
        }).then(result => {
            this.reportHtml = result;
        });
    },
    /**
     * Reload report.
     *
     * @private
     * @returns {Promise}
     */
    _reload: function () {
        return this._getHtml().then(() => {
            this.$('.o_content').html(this.reportHtml);
        });
    },

    _renderComponent: function () {
        const $buttons = $('<button>', {
            class: 'btn btn-primary',
            text: _t("Imprimer"),
        }).on('click', this._onClickPrint.bind(this));

        const $searchview = $(QWeb.render('pricelist_report_servette_music.report_pricelist_sm_search'));
        this.many2one.appendTo($searchview.find('.o_pricelist'));
        return { $buttons, $searchview };
    },


    _onClickAction: function (ev) {
        ev.preventDefault();
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            res_id: $(ev.currentTarget).data('res-id'),
            views: [[false, 'form']],
            target: 'self',

        });
    },

    _onClickPrint: function () {
        const reportName = _.str.sprintf('pricelist_report_servette_music.report_pricelist?active_model=%s&active_ids=%s&pricelist_id=%s&quantities=%s&with_ref=%s',
            this.context.active_model,
            this.context.active_ids,
            this.context.pricelist_id || '',
            '1',
            Boolean(this.context.with_ref),
        );

        return this.do_action({
            type: 'ir.actions.report',
            report_type: 'qweb-pdf',
            report_name: reportName,
            report_file: 'pricelist_report_servette_music.report_pricelist',
        });
    },

    _onFieldChanged: function (event) {
        this.context.pricelist_id = event.data.changes.pricelist_id.id;
        StandaloneFieldManagerMixin._onFieldChanged.apply(this, arguments);
        this._reload();
    },


});

core.action_registry.add('generate_pricelist_sm', GeneratePriceListSM);

return {
    GeneratePriceListSM,
};

});