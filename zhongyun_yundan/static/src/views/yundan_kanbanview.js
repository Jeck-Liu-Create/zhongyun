/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';
import { YundanDashBoard } from './yundan_dashboard';


export class YundanDashBoardKanbanRenderer extends KanbanRenderer {}

YundanDashBoardKanbanRenderer.template = 'yundan.PurchaseKanbanView';
YundanDashBoardKanbanRenderer.components= Object.assign({}, KanbanRenderer.components, {YundanDashBoard})

export const YundanDashBoardKanbanView = {
    ...kanbanView,
    Renderer: YundanDashBoardKanbanRenderer,
};

registry.category("views").add("yudnan_dashboard_kanban", YundanDashBoardKanbanView);
