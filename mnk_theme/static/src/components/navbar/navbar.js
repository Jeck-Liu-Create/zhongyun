/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";

import { useService } from "@web/core/utils/hooks";
import { bus, _t } from 'web.core';
import { Component, useState} from "@odoo/owl";

patch(NavBar.prototype, "mnk_theme.navbar_patch", {

    setup() {
        this._super(...arguments);
        this.sidebar_state = useState({ expand: false });
        this.appboardService = useService("mnk_app_board");

        // add sdiebar_sm to body
        if (!$('body').hasClass('sidebar_sm')) {
            $('body').addClass('sidebar_sm');
        }
    },

    _on_toggler_click() {
        if ($('body').hasClass('sidebar_sm')) {
            this.sidebar_state.expand = true;
            $('body').removeClass('sidebar_sm');
        } else {
            this.sidebar_state.expand = false;
            $('body').addClass('sidebar_sm');
        }
    },

    _isBoardVisible() {
        let $app_board = $(document.querySelector('.mnk_app_board'))
        return !$app_board.hasClass('d-none')
    },

    _on_board_togger_click(ev) {
        ev.preventDefault();
        if (!this._isBoardVisible()) {
            this.appboardService.show();
        } else {
            this.appboardService.hide();
        }
    }
})
