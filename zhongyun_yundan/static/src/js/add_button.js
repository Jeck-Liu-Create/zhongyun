odoo.define('lingqing_share.distribution_button', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {

                var btn = this.$buttons.find('.create_by_add_button');

                // 跳转到指定表单
                btn.on('click', () => {
                    console.log("点击事件")
                    var self = this;
                    var ks_button = $('.create_by_cx');
                    this._rpc({
                        "model": "zy.yundan.unit",
                        "method": "get_form_id",
                        "args":[],
                    }).then(function (data) {
                        console.log(data)
                        self.do_action({
                            res_model: 'zy.yundan.unit',
                            name: '补单',
                            views: [[data, 'form']],
                            view_mode: 'form',
                            target: 'current',
                            type: 'ir.actions.act_window',
                            tag: 'reload',
                            context: {
                               'default_replenish_state': true
                            },
                        },{
                            on_reverse_breadcrumb: function () {
                                ks_button.hide();
                                self.reload();
                            },
                            on_close: function () {
                                ks_button.hide();
                                self.reload();
                            }
                        })
                    });
                });
            }
        },
    
        _onSelectionChanged: function (event) {
            this._super.apply(this, arguments);
            var ks_button = $('.create_by_add_button');
            ks_button.show();
            this.renderer.selection.length !== 0 ? ks_button.show() : ks_button.hide();
        },

    });
});
