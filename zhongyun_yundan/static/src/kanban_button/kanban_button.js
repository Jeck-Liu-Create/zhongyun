/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { kanbanView } from '@web/views/kanban/kanban_view';
import { KanbanController } from '@web/views/kanban/kanban_controller';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';
import {AddDocumentUpload} from '../mixins/add_kanban';
import { registry } from "@web/core/registry";

export class AddKanbanController extends KanbanController {}
patch(AddKanbanController.prototype, 'add_kanban_controller_upload', AddDocumentUpload);

registry.category('views').add('add_button_kanban', {
    ...kanbanView,
    buttonTemplate: 'add.KanbanView.Buttons',
    Controller: AddKanbanController,
    Renderer:KanbanRenderer,

});

