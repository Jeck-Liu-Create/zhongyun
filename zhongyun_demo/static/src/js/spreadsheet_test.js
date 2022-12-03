/** @odoo-module **/

const { Component, EventBus, onWillStart, useSubEnv, useState } = owl;
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import Spreadsheet from "../../es6/index";



export class spreadsheet_test extends Component {

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.s = new Spreadsheet("#x-spreadsheet-demo")
          .loadData({}) // load data
          .change(data => {
            // save data to db
          });
    }
}

spreadsheet_test.template = "test_spreadsheet"

registry.category("actions").add("actions_spreadsheet", spreadsheet_test)


