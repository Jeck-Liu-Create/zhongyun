/** @odoo-module **/

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { luxonToMoment, momentToLuxon } from "@web/core/l10n/dates";
import { useService } from "@web/core/utils/hooks";

const { DateTime } = luxon;

import { Component, onWillStart, useExternalListener, useRef, useEffect} from "@odoo/owl";
const formatters = registry.category("formatters");
const parsers = registry.category("parsers");

export class DateRange extends Component {
    setup() {
        debugger
        this.notification = useService("notification");
        this.root = useRef("root");
        this.isPickerShown = false;
        this.pickerContainer;

        const jsDatestartDate = new Date('2022-03-21T08:00:00.000Z');
        this.myDateTimestartDate = DateTime.fromJSDate(jsDatestartDate);
        console.log(this.myDateTimestartDate.toISO());

        const jsDateendDate = new Date('2022-03-25T08:00:00.000Z');
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
                            format: 'YYYY/MM/DD'
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
    get formattedValue() {
        return this.formatValue(this.props.formatType, this.myDateTimestartDate);
    }
    get startDate() {
        return this.myDateTimestartDate
    }
    get endDate() {
        return this.myDateTimeendDate
    }
    formatValue(format, value) {
        const formatter = formatters.get(format);
        let formattedValue;
        try {
            formattedValue = formatter(value);
        } catch {
            console.log("this.props.record.setInvalidField(this.props.name);")
        }
        return formattedValue;
    }
    get inputvalue(){
        return this.value
    }

    updateRange(start, end) {
        console.log("updateRange")
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

    onPickerApply(ev, picker) {
        const start = this.isDateTime ? picker.startDate : picker.startDate.startOf("day");
        const end = this.isDateTime ? picker.endDate : picker.endDate.startOf("day");
        this.value = start.format('YYYY/MM/DD') + ' - ' + end.format('YYYY/MM/DD');
        this.root.el.value = this.value;
    }
    onPickerShow() {
        this.isPickerShown = true;
    }
    onPickerHide() {
        this.isPickerShown = false;
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


