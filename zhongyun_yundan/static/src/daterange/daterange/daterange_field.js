/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { luxonToMoment } from "@web/core/l10n/dates";
import { useService } from "@web/core/utils/hooks";
const { DateTime } = luxon;

import { Component, onWillStart, useExternalListener, useRef, useEffect} from "@odoo/owl";

export class DateRange extends Component {
    setup() {
        debugger
        this.notification = useService("notification");
        this.root = useRef("root");
        this.isPickerShown = false;
        this.pickerContainer;

        const jsDatestartDate = new Date('2023-03-21T08:00:00.000Z');
        this.myDateTimestartDate = DateTime.fromJSDate(jsDatestartDate);
        console.log(this.myDateTimestartDate.toISO());

        const jsDateendDate = new Date('2023-03-25T08:00:00.000Z');
        this.myDateTimeendDate = DateTime.fromJSDate(jsDateendDate);
        console.log(this.myDateTimeendDate.toISO());

        this.value="";

        useExternalListener(window, "scroll", this.onWindowScroll, { capture: true });
        onWillStart(() => loadJS("/web/static/lib/daterangepicker/daterangepicker.js"));
        useEffect(
            (el) => {
                if (el) {
                    window.$(el).daterangepicker({
                        timePicker: this.isDateTime,
                        timePicker24Hour: true,
                        timePickerIncrement: 5,
                        autoUpdateInput: false,
                        locale: {
                            applyLabel: this.env._t("Apply"),
                            cancelLabel: this.env._t("Cancel"),
                            customRangeLabel: '自定义',
                            format: 'YYYY-MM-DD'
                        },
                        ranges: {
                           "今天": [window.moment(), window.moment()],
                           "昨天": [window.moment().subtract(1, 'days'), window.moment().subtract(1, 'days')],
                           "过去7天": [window.moment().subtract(6, 'days'), window.moment()],
                           '过去30天': [window.moment().subtract(29, 'days'), window.moment()],
                           '当月': [window.moment().startOf('month'), window.moment().endOf('month')],
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
            () => [this.root.el, this.myDateTimestartDate]
        );
    }

    get isDateTime() {
        return this.props.formatType === "datetime";
    }

    get startDate() {
        return this.myDateTimestartDate
    }

    get endDate() {
        return this.myDateTimeendDate
    }

    get inputvalue(){
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
        this.value = start.format('YYYY-MM-DD') + ' ~ ' + end.format('YYYY-MM-DD');
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
            description:'建单时间介于'+ valueArray[0] + ' 00:00:00' + '和' + valueArray[2]  + ' 00:00:00' +'之间',
            domain:'["&",("establish_datetime", ">=", "' + valueArray[0] + ' 00:00:00' + '"),("establish_datetime", "<=", "' + valueArray[2] + ' 00:00:00' + '")]',
            type:'filter'}]
        this.env.searchModel.createNewFilters(preFilters);
    }
}

DateRange.props = {
    name: { type: String, optional: true},
    formatType: { type: String, optional: true },
};

DateRange.defaultProps = {
    name: { type: String, optional: true ,default:'测试名称'},
    formatType: { type: String, optional: true , default:'date'},
};
DateRange.template = "web.DateRange";


