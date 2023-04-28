/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { luxonToMoment } from "@web/core/l10n/dates";
import { useService } from "@web/core/utils/hooks";
const { DateTime } = luxon;

import { Component, onWillStart, useExternalListener, useRef, useEffect} from "@odoo/owl";

export class DateRange extends Component {
    setup() {
        debugger
        this.root = useRef("root");
        this.isPickerShown = false;
        this.searchBus = this.props.searchBus

        const jsDate = new Date();
        const luxonDate = DateTime.fromJSDate(jsDate, { zone: 'local' });
        this.zeroHour = luxonDate.startOf('day');
        console.log(this.zeroHour.toISO());
        this.endOfDay = luxonDate.endOf('day');
        console.log(this.endOfDay.toISO());
        this.value = this.zeroHour.toFormat('yyyy-MM-dd HH:mm:ss') + ' ~ ' + this.endOfDay.toFormat('yyyy-MM-dd HH:mm:ss');

        useExternalListener(window, "scroll", this.onWindowScroll, { capture: true });
        onWillStart(() => loadJS("/web/static/lib/daterangepicker/daterangepicker.js"));
        useEffect(
            (el) => {
                if (el) {
                    const today = window.moment();
                    const defaultStartTime = window.moment().startOf('day');
                    const defaultEndTime = today.clone().endOf('day');
                    window.$(el).daterangepicker({
                        timePicker: this.isDateTime,
                        timePicker24Hour: true,
                        timePickerIncrement: 5,
                        autoUpdateInput: false,
                        locale: {
                            applyLabel: this.env._t("Apply"),
                            cancelLabel: this.env._t("Cancel"),
                            customRangeLabel: '自定义',
                            format: 'YYYY-MM-DD HH:mm:ss'
                        },

                        ranges:{
                          "今天": [defaultStartTime, defaultEndTime],
                          "昨天": [window.moment().subtract(1, 'days').startOf('day'), window.moment().subtract(1, 'days').endOf('day')],
                          "过去7天": [window.moment().subtract(6, 'days').startOf('day'), defaultEndTime],
                          '过去30天': [window.moment().subtract(29, 'days').startOf('day'), defaultEndTime],
                          '当月': [window.moment().startOf('month'), today.clone().endOf('month')],
                          '上月': [window.moment().subtract(1, 'month').startOf('month'), window.moment().subtract(1, 'month').endOf('month')]
                        },
                        startDate: this.startDate ? luxonToMoment(this.startDate) : window.moment(),
                        endDate: this.endDate ? luxonToMoment(this.endDate) : window.moment(),
                        drops: "auto",
                    });
                    this.pickerContainer = window.$(el).data("daterangepicker").container[0];

                    window.$(el).on("apply.daterangepicker", this.onPickerApply.bind(this));
                    window.$(el).on("show.daterangepicker", this.onPickerShow.bind(this));
                    window.$(el).on("hide.daterangepicker", this.onPickerHide.bind(this));

                    this.pickerContainer.dataset.name = this.props.name;
                }

                return () => {
                    if (el) {
                        this.pickerContainer.remove();
                    }
                };
            },
            () => [this.root.el, this.zeroHour]
        );
    }

    get isDateTime() {
        return true;
    }

    get startDate() {
        // 当日零点
        return this.zeroHour
    }

    get endDate() {
        // 当日二十四点
        return this.endOfDay
    }

    get inputValue(){
        return this.value
    }

    onWindowScroll(ev) {
        const target = ev.target;
        if (
            this.isPickerShown &&
            !this.env.isSmall &&
            (target === window || !this.pickerContainer.contains(target))
        ) {
            window.$(this.root.el).data("daterangepicker").hide();
        }
    }

    onChangeInput(ev) {
        this.value = ev.target.value;
        this.render();
    }

    onPickerApply(ev, picker) {
        debugger;
        const start = this.isDateTime ? picker.startDate : picker.startDate.startOf("day");
        const end = this.isDateTime ? picker.endDate : picker.endDate.startOf("day");
        this.value = start.format('YYYY-MM-DD HH:mm:ss') + ' ~ ' + end.format('YYYY-MM-DD HH:mm:ss');
        this.root.el.value = this.value;
        this.render();
    }
    onPickerShow() {
        this.isPickerShown = true;
    }
    onPickerHide() {
        this.isPickerShown = false;
    }

    onApply() {
        this.env.searchModel.query = [];
        const value = this.value
        const valueArray = value.split(' ')
        const preFilters = [{
            description:'建单时间介于'+ valueArray[0] + ' ' + valueArray[1] + '和' + valueArray[3] + ' ' + valueArray[4] +'之间',
            domain:'["&",("establish_datetime", ">=", "' + valueArray[0] + ' ' + valueArray[1] +'"),("establish_datetime", "<=", "' + valueArray[3] + ' ' + valueArray[4] + '")]',
            type:'filter'}]
        this.env.searchModel.createNewFilters(preFilters);
    }
}

DateRange.props = {
    name: { type: String, optional: true},
    formatType: { type: String, optional: true },
    searchBus: Object
};

DateRange.defaultProps = {
    name: { type: String, optional: true ,default:'测试名称'},
    formatType: { type: String, optional: true , default:'date'},
};
DateRange.template = "web.DateRange";


