odoo.define('tu_modulo.tu_script', function (require) {
    "use strict";
    
    var core = require('web.core');
    var _t = core._t;
    
    var FormView = require('web.FormView');
    
    FormView.include({
        on_load: function (fields_view) {
            this._super.apply(this, arguments);
            
            // Ejecuta tu acción aquí
            if (fields_view.model === 'hp_hotel.reservaciones') {
                console.log('La vista de reservaciones se ha cargado.');
                // Llama a tu método personalizado aquí
                this.rpc('/web/dataset/call_kw/hp_hotel.reservaciones/ejecutar_accion', {
                    model: 'hp_hotel.reservaciones',
                    method: 'ejecutar_accion',
                    args: [[]],
                    kwargs: {},
                });
            }
        },
    });
});
