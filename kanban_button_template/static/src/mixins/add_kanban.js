/** @odoo-module **/

import { useBus, useService, } from '@web/core/utils/hooks';

const { onWillStart ,useRef} = owl;

export const AddDocumentUpload = {
    setup() {
        this._super();
        this.actionService = useService('action');
        this.orm = useService('orm');
        this.root = useRef("root");
        // onWillStart(this.onWillStart);
        onWillStart(async () => {
            const action = await this.orm.call('zy.yundan.unit', 'add_kanban_button',[]);
            console.log(action);
            // this.state.expenses = action;
        });

    },
    // async uploadDocument() {
    //     debugger
    //     const action = await this.orm.call('zy.yundan.uint', 'button_replenish', []);
    //     this.actionService.doAction(action);
    // },

    // async onWillStart() {
    //     const action = await this.orm.call('zy.yundan.unit', 'add_kanban_button',[]);
    //
    //     console.log('action');
    //     // this.actionService.doAction(action);
    // },

    // uploadDocument() {
    //     this.fileInput.el.click();
    // },
    //
    // async onChangeFileInput() {
    //     const params = {
    //         csrf_token: odoo.csrf_token,
    //         ufile: [...this.fileInput.el.files],
    //         model: 'hr.expense',
    //         id: 0,
    //     };
    //
    //     const fileData = await this.http.post('/web/binary/upload_attachment', params, "text");
    //     const attachments = JSON.parse(fileData);
    //     if (attachments.error) {
    //         throw new Error(attachments.error);
    //     }
    //     this.onUpload(attachments);
    // },
    //
    // async onUpload(attachments) {
    //     const attachmentIds = attachments.map((a) => a.id);
    //     if (!attachmentIds.length) {
    //         this.notification.add(
    //             this.env._t('An error occurred during the upload')
    //         );
    //         return;
    //     }
    //
    //     const action = await this.orm.call('hr.expense', 'create_expense_from_attachments', ["", attachmentIds]);
    //     this.actionService.doAction(action);
    // },
};
