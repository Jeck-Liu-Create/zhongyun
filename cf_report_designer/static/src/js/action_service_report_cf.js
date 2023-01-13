/** @odoo-module */
import { registry } from "@web/core/registry";
import { ComponentAdapter } from "web.OwlCompatibility";
const { Component } = owl;
import { _lt } from "@web/core/l10n/translation";

/**
 * CFPrint打印类
 * ver 1.3
 * 康虎软件工作室
 * Email: wdmsyf@sina.com
 * QQ: 360026606
 * 微信: 360026606
 */
/**
 * websocket部分可以抵用下面这个：
 * https://jsrepos.com/lib/vitalets-websocket-as-promised-javascript-websocket
 */

/**
 *
 * @param SOCKET_URL
 * @returns {Promise<unknown>|Promise<WebSocket>}
 */
function getSocket(SOCKET_URL) {
    if (getSocket.server && getSocket.server.readyState < 2) {
        console.log("reusing the socket connection [state = " + getSocket.server.readyState + "]: " + getSocket.server.url);
        return Promise.resolve(getSocket.server);
    }

    return new Promise(function (resolve, reject) {
        getSocket.server = new WebSocket(SOCKET_URL);

        getSocket.server.onopen = function () {
            console.log("socket connection is opened [state = " + getSocket.server.readyState + "]: " + getSocket.server.url);
            resolve(getSocket.server);
        };
        getSocket.server.onmessage = function(event){
            var dat = event.data;
            console.log("接收到打印伺服器信息：\n"+dat);
            var datJson = JSON.parse(dat);
			/**
			 * 这里可以增加打印成功回调函数
			 */
        };
        getSocket.server.onerror = function (err) {
            console.error("socket connection error : ", err);
            reject(err);
        };
    });
};

/**
 * 打印数据发送到打印伺服器
 * @param data
 * @private
 */
function sendToCFPrint(data, env){
	let self = this;
	let _rptData = data.data || '';
	let _delay_send = data._delay_send || 1000;            //发送打印服务器前延时时长,-1表示不自动发送
	let _delay_close = data.delay_close || 1000;           //打印完成后关闭窗口的延时时长, -1则表示不关闭
	let cfprint_addr = data.address || "127.0.0.1";    //打印服务器的地址
	let cfprint_port = data.port || 54321;          //打印服务器监听端口

	let url = "ws://"+cfprint_addr+":"+cfprint_port;

	getSocket(url).then(function(server) {
		console.log("报表数据发送到打印伺服器...");
		server.send(_rptData);
		env.services.notification.add(
			_lt("报表已发送到打印伺服器。\n如果打印机未输出报表，请检查打印伺服器提示信息。"),
			{
				sticky: false,
				title: env._t("Report"),
			}
		);
	}).catch(function(err) {
		console.error("打印报表失败。"+err);
		env.services.notification.add(
			_lt("打印报表失败。")+err.message,
			{
				sticky: false,
				title: env._t("Report"),
			}
		);
	});
};

/**
 * 自定义报表handler
 * handler在 web/static/src/webclient/actions/action_service.js 中 _executeReportAction 方法中调用
 *
 * @param action
 * @param options
 * @param env
 * @returns {Promise<boolean|*>}
 * @constructor
 */
async function CFReportActionHandler(action, options, env) {
/*
    if (action.device_id) {
        // Call new route that sends you report to send to printer
        const orm = env.services.orm;
        const args = [action.id, action.context.active_ids, { device_id: action.device_id }];
        const [ip, identifier, document] = await orm.call("ir.actions.report", "iot_render", args);
        const adapterParent = new ComponentAdapter(null, { Component }); // For trigger_up and service calls
        const iotDevice = new DeviceProxy(adapterParent, { iot_ip: ip, identifier });
        iotDevice.add_listener(data => onValueChange(data, env));
        iotDevice.action({ document })
            .then(data => onIoTActionResult(data, env))
            .guardedCatch(() => adapterParent.call("iot_longpolling", "_doWarnFail", ip));
        return true;
    }
*/

	var self = this;
	const type = action.report_type;
	const actionContext = action.context || {};
	var isDesign = false;
	if(actionContext) {
		isDesign = actionContext.is_design;
	}
	if (type === 'qweb-html' && !isDesign && (action.cf_report_define_id || action.report_name.startsWith("cf_report_designer."))) {
		console.info("处理康虎云报表");
		let url = `/report/${type}/${action.report_name}`;

		env.services.ui.block();
    	var def = $.Deferred();
		var blocked = !env.services.rpc('/cfreport/download', {
			data: {url: url, type: type, report_name:action.report_name, context: actionContext},
			token: 'dummy-because-api-expects-one',
			context: actionContext,
		}).then(function (result) {
			console.debug("下载康虎云报表数据成功。 \n" + result);
			sendToCFPrint(result, env);
		}).catch(function (error){
			console.error('打印报表失败', error);
			throw error;
        }).finally(function() {
			env.services.ui.unblock();
        });
    	return def;
	}
}

registry
    .category("ir.actions.report handlers")
    .add("cf_report_action_handler", CFReportActionHandler);
