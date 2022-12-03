odoo.define('echart_views.Model', function (require) {
    'use strict';

    var AbstractModel = require('web.AbstractModel');

    var EchartModel = AbstractModel.extend({
        /**
         * 该方法需要返回renderer所需的数据
         * 数据可以通过load/reload执行相关获取数据方法时，设置到该对象上
         */
        get: function () {
            console.log("eview model >>> get");
            this._super();
        },
        /**
         * 只会初次加载时执行一次，需要自定义相关数据获取方法获取数据并设置到该对象上
         *
         * @param {Object} params
         * @param {string} params.modelName the name of the model
         * @returns {Deferred} The deferred resolves to some kind of handle
         */
        load: function (params) {
            console.log("eview model >>> load");
            return this._super.apply(this, arguments);
        },
        /**
         * 当有相关数据变动时，重新获取数据。
         *
         * @param {Object} params
         * @returns {Deferred}
         */
        reload: function (handle, params) {
            console.log("eview model >>> reload");
            return this._super.apply(this, arguments);
        },
    });

    return EchartModel;

});