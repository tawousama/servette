odoo.define('point_of_sale.field_many2many_tags', function (require) {
    'use strict';

    const {useState, useExternalListener} = owl;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class FieldMany2ManyTags extends PosComponent {
        constructor() {
            super(...arguments);
            this.value = this.props.value || [];
            this.model = this.props.model;
            this.tags = {};
            this.create_new = false;
            this.env.pos.tags.forEach(el=> this.tags[el.id] = el);
            const tags = this.props.value;
            console.log('+++++++++++++++++++++++++')
            console.log(tags)
            this.colorField = this.props.color_field || 'color';
            this.state = useState({
                showDropdown: false,
                changes: this.props.changes,
                tags_list: [],
            });
            this._refresh_tags_list()
            this.search = undefined;
            useExternalListener(window, 'click', this._onClickHideDropdown);
        }
        mounted() {
            this.$input = $(this.el).find('.tag_input');
        }
        _refresh_tags_list() {
            let tags_list = []
            let count = 0
            let max = 5
            this.props.tags.forEach(el=> {
                let index
                if (this.value) {
                    index = this.value.indexOf(el.id);
                } else {
                    index = -1
                }
                if (index <= -1 && count <= max && (!this.search || el.display_name.toLowerCase().includes(this.search.toLowerCase()))) {
                    tags_list.push(el)
                    count += 1
                }

            })
            let all_tags_name = []
            this.props.tags.forEach(el=> all_tags_name.push(el.display_name))
            this.create_new = !!(this.search && all_tags_name.indexOf(this.search) === -1);
            this.state.tags_list = tags_list
        }
        _showDropdown() {
            this.state.showDropdown = true;
        }
        _onClickHideDropdown(ev) {
//            if (!$(ev.target).closest('.tag_dropdown-item, .o_input_dropdown').length) {
//                this._hideDropdown()
//            }
        }
        _hideDropdown() {
            this.state.showDropdown = false;
        }
        _onClickTag(id) {
            this._hideDropdown()
            this.value.push(id)
            this.state.changes['category_id'] = this.value
            this.search = undefined
            this.$input.val('')
            this._refresh_tags_list()
        }
        _onClickDeleteTag(id) {
            const index = this.value.indexOf(id);
            if (index > -1) {
              this.state.changes['category_id'] = this.value.splice(index, 1);
            }
            this._refresh_tags_list()
        }
        _onChange(event) {
            if (event.target.value !== undefined) {
                this.search = event.target.value;
            } else {
                this.search = undefined;
            }
            this._refresh_tags_list();
        }
        async _onClickCreateNewTag(event) {
            try {
                let tag = await this.rpc({
                    model: this.model,
                    method: 'create_from_ui',
                    args: [{name: this.search}],
                });
                this.props.tags.push(tag);
                this.tags[tag.id] = tag;
                this._onClickTag(tag.id);
                this.search = undefined;
                this.$input.val('');
                this.render();
            } catch (error) {
                if (error.message.code < 0) {
                    await this.showPopup('OfflineErrorPopup', {
                        title: this.env._t('Offline'),
                        body: this.env._t('Unable to save changes.'),
                    });
                } else {
                    throw error;
                }
            }
        }
    }
    FieldMany2ManyTags.template = 'pos_custom.FieldMany2ManyTags';
    Registries.Component.add(FieldMany2ManyTags);

});
