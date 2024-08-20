odoo.define('pos_custom.PartnerDetailsEdit', function(require) {
    'use strict';

    const { _t } = require('web.core');
    const { getDataURLFromFile } = require('web.utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    var PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');

    const SMPartnerDetailsEdit = PartnerDetailsEdit => class extends PartnerDetailsEdit {
         constructor() {
                super(...arguments);
                console.log(this.intFields)
//                this.intFields.push('zip_id');
                const partner = this.props.partner;
//                const tags = this.props.partner.category_id;

//                console.log('=+=++==++==++=partner=+=+=+=+=+=+=+=+=+')
//                console.log(partner.firstname)
//                console.log('=+=++==++==++=tags+=+=+=+=+=+=+=+')
//                console.log(tags)
//
//                const alltags = this.env.pos.tags
//                console.log('=+=++==++==++= all tags+=+=+=+=+=+=+=+')
//                console.log(alltags)
//                const res = alltags.filter(({id}) => tags.includes(id));
//                console.log(res)

            }

         _OnChangeName(event) {
                var firstname = $('.partner-firstname').val();
                var lastname = $('.partner-lastname').val();
                if (this.props.partner.type === 'contact' || !this.props.partner.type)
                {
                    if (firstname){
                        firstname = firstname.charAt(0).toUpperCase() + firstname.slice(1);
                    }
                    if (lastname){
                        lastname = lastname.toUpperCase();
                    }
                }
                 $('.partner-name').val(lastname + ' '+ firstname);
                this.changes[event.target.name] = event.target.value;
            }

        saveChanges() {
                var zip_id = this.props.partner.zip_id || false;

                var obj_zip = $(".client-address-location-completion option:selected");

                var change_zip_id = obj_zip.val();
                console.log('=+=++==++==++=SAVE=+=+=+=+=+=+=+=+=+');
                console.log(change_zip_id);

                if ((zip_id && parseInt(change_zip_id) !== parseInt(zip_id.id)) ||
                (!zip_id && change_zip_id && change_zip_id!==''))
                {
                    this.changes["zip_id"] = parseInt(change_zip_id);
                    this.changes["zip"] =  $(".detail").eq(7).val();
                    this.changes["city"] = $(".detail").eq(6).val();
                    this.changes["country_id"] = $(".detail").eq(9).val();
                    this.changes["state_id"]= $(".detail").eq(8).val();


                }



                let processedChanges = {};
                for (let [key, value] of Object.entries(this.changes)) {
                    if (this.intFields.includes(key)) {
                        console.log('=+=++==++==++=processed changes=+=+=+=+=+=+=+=+=+');
                        console.log(key);
                        console.log(value);
                        processedChanges[key] = parseInt(value) || false;
                    } else {
                        console.log('=+=++==++==++=processed changes=+=+=+=+=+=+=+=+=+');
                        console.log(key);
                        console.log(value);
                        processedChanges[key] = value;
                    }
                }

                if (((!this.props.partner.firstname  && !processedChanges.firstname) || processedChanges.firstname === '') &&
                ((!this.props.partner.lastname  && !processedChanges.lastname) || processedChanges.lastname === '')


                )
                {
                    return this.showPopup('ErrorPopup', {
                      title: _t('A Customer Firstname or Lastname Is Required'),
                    });
                }
                processedChanges.id = this.props.partner.id || false;
                this.trigger('save-changes', { processedChanges });
            }

        };

        Registries.Component.extend(PartnerDetailsEdit, SMPartnerDetailsEdit);
        return PartnerDetailsEdit;

});


