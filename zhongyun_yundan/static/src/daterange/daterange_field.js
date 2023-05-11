/** @odoo-module **/
import {loadJS} from "@web/core/assets";
import {luxonToMoment, deserializeDate,serializeDateTime} from "@web/core/l10n/dates";
import {Component, onWillStart, useEffect, useExternalListener, useRef} from "@odoo/owl";


const { DateTime } = luxon;

export class DateRange extends Component {
    setup() {
        debugger
        this.root = useRef("root");
        this.isPickerShown = false;
        this.selectValue = 'establish_datetime';
        this.searchBus = this.props.searchBus;
        const jsDate = new Date();
        const luxonDate = DateTime.fromJSDate(jsDate, { zone: 'local' });
        this.zeroHour = luxonDate.startOf('day');
        this.endOfDay = luxonDate.endOf('day');
        this.value = this.zeroHour.toFormat('yyyy-MM-dd HH:mm:ss') + ' ~ ' + this.endOfDay.toFormat('yyyy-MM-dd HH:mm:ss');
        this.evnShearch()
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
                        autoUpdateInput: true,
                        timePickerSeconds: true,
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

    // 同步select值变化
    changeParam(ev) {
        this.selectValue = ev.target.value;
        this.evnShearch()
    }

    // 同步input值变化
    evnShearch(){
        const envValue= this.value;
        const name = '1';
        console.log(envValue)
        console.log(this.datetime)
        this.searchBus.trigger('searchList', {field: this.selectValue, filters:this.datetime , id:name});
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
        this.evnShearch()
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

    get datetime(){
        debugger
        const envValue= this.value;
        const valueArray = envValue.split(' ')
        const startTime = deserializeDate(valueArray[0] + ' ' + valueArray[1])
        const endTime = deserializeDate(valueArray[3] + ' ' + valueArray[4])
        const domain = '"&",("establish_datetime", ">=", "' + startTime.setZone('utc').toFormat('yyyy-MM-dd HH:mm:ss') +'"),("establish_datetime", "<=", "' + endTime.setZone('utc').toFormat('yyyy-MM-dd HH:mm:ss') + '")'
        return {valueArray,startTime,endTime,domain}
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


