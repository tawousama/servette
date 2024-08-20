// odoo.define('my_module.change_css', function (require) {

//     "use strict";
  
  
//     var core = require('web.core');
  
//     var QWeb = core.qweb;
  
  
//     $(document).ready(function () {
        
  
//         $('h6.o_wsale_products_item_title a').attr('style', 'color: red !important');

  
//     });

//   });

// widget 

odoo.define('my_module.change_css', function (require) {
    "use strict";

    var Widget = require('web.Widget');

    var MyWidget = Widget.extend({
        // Override the `start` method to make changes after the widget is rendered
        inserted: function () {
            
        
            this.$el.prependTo('body'); // Add the widget to the body before anything else
        
            $('h6.o_wsale_products_item_title a').attr('style', 'color: green !important');
            alert("lol77");

            var def = this._super.apply(this, arguments);
            
            return def;
        },
    });

    var myWidgetInstance = new MyWidget(); // Instantiate the widget
    myWidgetInstance.appendTo($('body')); // Append the widget to the body or a specific element

    return MyWidget;
});