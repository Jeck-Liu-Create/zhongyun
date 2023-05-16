/** @odoo-module **/

import { useBus, useService } from '@web/core/utils/hooks';

const { onWillStart ,useState} = owl;

export const AddDocumentUpload = {
    setup() {

        this.actionService = useService('action');
        this.orm = useService('orm');
        this.state = useState({
            action: {}
        });

        // onWillStart(this.onWillStart);
        onWillStart(async () => {
            const action = await this.orm.call('zy.yundan.unit', 'add_kanban_button',[]);
            console.log(action);
            this.state.action = action;
        });

    },
    replenishButton() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            view_type: 'form',
            view_mode: "form",
            res_id: false,
            res_model: 'zy.yundan.unit',
            name: '补单组',
            context: {'default_replenish_state': true},
            // target: "new",
            views: [[this.state.action.data.id, "form"]],
        });
        // return this.actionService.doAction{}
    },

};
