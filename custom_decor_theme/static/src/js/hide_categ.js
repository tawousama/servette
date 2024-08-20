


odoo.define('custom_decor_theme.demande_info', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    const {Markup} = require('web.utils');

    var _t = core._t;

  


    publicWidget.registry.ServetteDemandeInfo = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        events: {
            'click #demande_info_submit': 'demandeInfo',
            'click .demande_info_button': 'demandeInfo_prepare',
            'click #demande_info_close': 'demandeInfo_close',
           
        },

        
      
        
        demandeInfo_prepare: function(e){

            if ($('#product_details>h1').length) {
                $('#demandeInfoForm > div > #product_template_name').val($('#product_details>h1').html())
               
            } else {
                 $('#demandeInfoForm > div > #product_template_name').val(e['currentTarget'].parentNode.children[0].children[0].innerText)
            }
            
            $('#demandeInfoForm > input#product_template_id').val(e['currentTarget'].parentNode.children['product_id'].value)
            
            $('#demandeInfoModal').modal('show');
        },
        
        
        demandeInfo_close: function(e){
            $('#demandeInfoModal').modal('hide')
            $('#demandeInfoModal input, #demandeInfoModal textarea').val('')
            $('#demandeInfoModal #indifferent').prop('checked', true);
            $("#warningMessage").html('');
        },
        
        demandeInfo: function (e) {
            e.preventDefault();
           
            var requiredInputs = document.querySelectorAll('input[required], textarea[required]');
            var alertMessage = '';
            var incompleteFields = [];
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    
            const isValidEmail = emailRegex.test($('#email2').val());
            requiredInputs.forEach(function(input) {
              if (!input.value.trim()) {
                incompleteFields.push(input.name);
              }
            });
          
            if (incompleteFields.length > 0) {
              alertMessage = 'Completer les champs suivant: ' + incompleteFields.join(', ');
              $("#warningMessage").html(alertMessage);
            }
            else if (!isValidEmail) {
                alertMessage = 'Email invalide';
                $("#warningMessage").html(alertMessage);
            }
            else {
            $('#loadingdiv').css('display','flex')
            var choix_contact = '';
            var checkedRadioButton = document.querySelector('input[name="guest_choix"]:checked');
            if (checkedRadioButton) {
                
                choix_contact = checkedRadioButton.attributes['valeur'].value;
                
            } 
            this._rpc({
                route: '/servette/request_info',
                params: {
                    'csrf_token': core.csrf_token,
                    'product': document.getElementById("product_template_name").value,
                    'product_id': $('#demandeInfoForm > input#product_template_id').val(),
                    'name': document.getElementById("name2").value,
                    'email': document.getElementById("email2").value,
                    'phone': document.getElementById("phone2").value,
                    'question': document.getElementById("guest_questions").value,
                    'choix_contact': choix_contact
                    
                }
            }).then(function(data) {
                if(data.success) {
                    
                    $('#loading').hide()
                    $('#loadingsuccess').show();
                    setTimeout(function() {
                        $('#demande_info_close').click();
                        $('#loadingdiv').css('display','none');
                        $('#loading').show()
                        $('#loadingsuccess').hide();
                      }, 5000);
                    
                }
              

            })

            }
            
          },
        
        
    });

    return publicWidget.registry.ServetteDemandeInfo;
});
