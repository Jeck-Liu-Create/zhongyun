/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { YundanDashBoard } from './yundan_dashboard';
import {DateRange} from "../daterange/daterange_field";
import { useBus, useService } from '@web/core/utils/hooks';
import { onWillStart, useRef, useState, EventBus } from "@odoo/owl";

const FIELD_CLASSES = {
    char: "o_list_char",
    float: "o_list_number",
    integer: "o_list_number",
    monetary: "o_list_number",
    text: "o_list_text",
    many2one: "o_list_many2one",
};

export class YundanDashBoardRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.envBus = new EventBus();
        this.envBus.on('SearchList', this, this.searchChange);
        this.query = {};
    }

    searchChange({field, filters}) {
        this.query[field.id] = {field, filters};
    }

    getColumnClass(column) {
        const classNames = ["align-middle"];
        if (column.id === "column_0"){
                classNames.push("listTh_0")
            }
        if (column.id === "column_1"){
            classNames.push("listTh_1")
        }
        if (column.name === 'state'){
            classNames.push("listTh_state")
        }
        if (this.isSortable(column)) {
            classNames.push("o_column_sortable", "position-relative", "cursor-pointer");
        } else {
            classNames.push("cursor-default");
        }
        const orderBy = this.props.list.orderBy;
        if (
            orderBy.length &&
            column.widget !== "handle" &&
            orderBy[0].name === column.name &&
            column.hasLabel
        ) {
            classNames.push("table-active");
        }
        if (this.isNumericColumn(column)) {
            classNames.push("o_list_number_th");
        }
        if (column.type === "button_group") {
            classNames.push("o_list_button");
        }
        if (column.widget) {
            classNames.push(`o_${column.widget}_cell`);
        }

        return classNames.join(" ");
    }

    getCellClass(column, record) {
        if (!this.cellClassByColumn[column.id]) {
            const classNames = ["o_data_cell"];
            if (column.type === "button_group") {
                classNames.push("o_list_button");
            } else if (column.type === "field") {
                classNames.push("o_field_cell");
                if (
                    column.rawAttrs &&
                    column.rawAttrs.class &&
                    this.canUseFormatter(column, record)
                ) {
                    classNames.push(column.rawAttrs.class);
                }
                const typeClass = FIELD_CLASSES[this.fields[column.name].type];
                if (typeClass) {
                    classNames.push(typeClass);
                }
                if (column.widget) {
                    classNames.push(`o_${column.widget}_cell`);
                }
            }
            if (column.id === "column_0"){
                classNames.push("listRow_0")
            }
            if (column.id === "column_1"){
                classNames.push("listRow_1")
            }
            if (column.name === "state"){
                classNames.push("listRow_state")
            }
            this.cellClassByColumn[column.id] = classNames;
        }
        const classNames = [...this.cellClassByColumn[column.id]];
        if (column.type === "field") {
            if (record.isRequired(column.name)) {
                classNames.push("o_required_modifier");
            }
            if (record.isInvalid(column.name)) {
                classNames.push("o_invalid_cell");
            }
            if (record.isReadonly(column.name)) {
                classNames.push("o_readonly_modifier");
            }
            if (this.canUseFormatter(column, record)) {
                // generate field decorations classNames (only if field-specific decorations
                // have been defined in an attribute, e.g. decoration-danger="other_field = 5")
                // only handle the text-decoration.
                const { decorations } = record.activeFields[column.name];
                for (const decoName in decorations) {
                    if (evaluateExpr(decorations[decoName], record.evalContext)) {
                        classNames.push(getClassNameFromDecoration(decoName));
                    }
                }
            }
            if (
                record.isInEdition &&
                this.props.list.editedRecord &&
                this.props.list.editedRecord.isReadonly(column.name)
            ) {
                classNames.push("text-muted");
            } else {
                classNames.push("cursor-pointer");
            }
        }
        return classNames.join(" ");
    }

}

YundanDashBoardRenderer.template = 'Yundan.PurchaseListView';
YundanDashBoardRenderer.recordRowTemplate = "Yundan.ListRenderer.RecordRow";
YundanDashBoardRenderer.components= Object.assign({}, ListRenderer.components, {YundanDashBoard,DateRange})

export const YundanDashBoardListView = {
    ...listView,
    Renderer: YundanDashBoardRenderer,
};

registry.category("views").add("yundan_dashboard_list", YundanDashBoardListView);
