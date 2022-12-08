const {Component, xml} = owl;
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

class AddKanbanButton extends Component {
    setup() {
        this.actionService = useService("action");
    }

    onClickCreate() {
        this.actionService.doAction({
            name: "运单组补单",
            res_model: "res.users",
            views: [[false, "list"]],
            type: "ir.actions.act_window",
            view_mode: "form",
            target: 'new'
        })
    }

}
AddKanbanButton.template = 'add.KanbanView.Buttons';

registry.category('actions').add('AddKanbanButton', AddKanbanButton);
