odoo.define('cf_sql_report.add_sql_model_button', function (require) {
"use strict";

var core = require('web.core');
var FormController = require('web.FormController');
FormController.include({
    renderButtons: function ($node) {
        this._super.apply(this, arguments);
        if (this.$buttons) {
            this.$buttons.find('.o_car_store_sync_data_button').click(this.proxy('action_sync_data'));
            this.$buttons.on('click', '.o_cf_report_add_sql_model_button', this._onAddSQLModel.bind(this));
        }
    },

    //--------------------------------------------------------------------------
    // Define Handler for new Custom Button
    //--------------------------------------------------------------------------

    /**
     * Called when the user wants to create a new record -> @see createRecord
     *
     * @private
     */
    _onAddSQLModel: function () {
        // this.createRecord();
        var self = this;
        return self._rpc({
            model: "cf.report.define",
            method: "action_create_sql_model",
            args: [false],
            context: [],
        }).then(function(action){
            return self.do_action(action);
        });
    },

});
// viewRegistry.add('hr_employee_profile_form', EmployeeProfileFormView);
// return EmployeeProfileFormView;

});