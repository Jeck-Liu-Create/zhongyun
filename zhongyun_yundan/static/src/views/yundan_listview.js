/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { YundanDashBoard } from './yundan_dashboard';

export class YundanDashBoardRenderer extends ListRenderer {};

YundanDashBoardRenderer.template = 'Yundan.PurchaseListView';
YundanDashBoardRenderer.components= Object.assign({}, ListRenderer.components, {YundanDashBoard})

export const YundanDashBoardListView = {
    ...listView,
    Renderer: YundanDashBoardRenderer,
};

registry.category("views").add("yundan_dashboard_list", YundanDashBoardListView);
