odoo.define('zhongyun_demo.x_spreadsheet', function (require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction')
    var core = require('web.core')
    var spreadsheet = AbstractAction.extend({
        template: 'x_spreadsheet',
        // 初始化，可以在action 里传入参数
        init: function (parent, action, option) {
          // 保存传递的参数
          this._super.apply(this, arguments);
          var options = action.params || {};
          this.params = options;  // NOTE forwarded to embedded client action
          console.log('测试数据:' ,this.params);
        },

        start: function (parent, action) {
            var self = this
            console.log('this:' ,self); 
            var data_other = this.params
            console.log('测试数据2:' ,data_other.id);
            $(document).ready(function () {
            // window.onload = function() {
                window&&window.x_spreadsheet&&(window.x_spreadsheet.$messages=window.x_spreadsheet.$messages||{},window.x_spreadsheet.$messages["zh-cn"]={toolbar:{undo:"撤销",redo:"恢复",print:"打印",paintformat:"格式刷",clearformat:"清除格式",format:"数据格式",fontName:"字体",fontSize:"字号",fontBold:"加粗",fontItalic:"倾斜",underline:"下划线",strike:"删除线",color:"字体颜色",bgcolor:"填充颜色",border:"边框",merge:"合并单元格",align:"水平对齐",valign:"垂直对齐",textwrap:"自动换行",freeze:"冻结",autofilter:"自动筛选",formula:"函数",more:"更多"},contextmenu:{copy:"复制",cut:"剪切",paste:"粘贴",pasteValue:"粘贴数据",pasteFormat:"粘贴格式",hide:"隐藏",insertRow:"插入行",insertColumn:"插入列",deleteSheet:"删除",deleteRow:"删除行",deleteColumn:"删除列",deleteCell:"删除",deleteCellText:"删除数据",validation:"数据验证",cellprintable:"可打印",cellnonprintable:"不可打印",celleditable:"可编辑",cellnoneditable:"不可编辑"},print:{size:"纸张大小",orientation:"方向",orientations:["横向","纵向"]},format:{normal:"正常",text:"文本",number:"数值",percent:"百分比",rmb:"人民币",usd:"美元",eur:"欧元",date:"短日期",time:"时间",datetime:"长日期",duration:"持续时间"},formula:{sum:"求和",average:"求平均值",max:"求最大值",min:"求最小值",concat:"字符拼接",_if:"条件判断",and:"和",or:"或"},validation:{required:"此值必填",notMatch:"此值不匹配验证规则",between:"此值应在 {} 和 {} 之间",notBetween:"此值不应在 {} 和 {} 之间",notIn:"此值不在列表中",equal:"此值应该等于 {}",notEqual:"此值不应该等于 {}",lessThan:"此值应该小于 {}",lessThanEqual:"此值应该小于等于 {}",greaterThan:"此值应该大于 {}",greaterThanEqual:"此值应该大于等于 {}"},error:{pasteForMergedCell:"无法对合并的单元格执行此操作"},calendar:{weeks:["日","一","二","三","四","五","六"],months:["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"]},button:{next:"下一步",cancel:"取消",remove:"删除",save:"保存",ok:"确认"},sort:{desc:"降序",asc:"升序"},filter:{empty:"空白"},dataValidation:{mode:"模式",range:"单元区间",criteria:"条件",modeType:{cell:"单元格",column:"列模式",row:"行模式"},type:{list:"列表",number:"数字",date:"日期",phone:"手机号",email:"电子邮件"},operator:{be:"在区间",nbe:"不在区间",lt:"小于",lte:"小于等于",gt:"大于",gte:"大于等于",eq:"等于",neq:"不等于"}}});
                x_spreadsheet.locale('zh-cn');
                var saveIcon = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/PjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+PHN2ZyB0PSIxNTc3MTc3MDkyOTg4IiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjI2NzgiIHdpZHRoPSIxOCIgaGVpZ2h0PSIxOCIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPjxkZWZzPjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+PC9zdHlsZT48L2RlZnM+PHBhdGggZD0iTTIxMy4zMzMzMzMgMTI4aDU5Ny4zMzMzMzRhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMSA4NS4zMzMzMzMgODUuMzMzMzMzdjU5Ny4zMzMzMzRhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMS04NS4zMzMzMzMgODUuMzMzMzMzSDIxMy4zMzMzMzNhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMS04NS4zMzMzMzMtODUuMzMzMzMzVjIxMy4zMzMzMzNhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMSA4NS4zMzMzMzMtODUuMzMzMzMzeiBtMzY2LjkzMzMzNCAxMjhoMzQuMTMzMzMzYTI1LjYgMjUuNiAwIDAgMSAyNS42IDI1LjZ2MTE5LjQ2NjY2N2EyNS42IDI1LjYgMCAwIDEtMjUuNiAyNS42aC0zNC4xMzMzMzNhMjUuNiAyNS42IDAgMCAxLTI1LjYtMjUuNlYyODEuNmEyNS42IDI1LjYgMCAwIDEgMjUuNi0yNS42ek0yMTMuMzMzMzMzIDIxMy4zMzMzMzN2NTk3LjMzMzMzNGg1OTcuMzMzMzM0VjIxMy4zMzMzMzNIMjEzLjMzMzMzM3ogbTEyOCAwdjI1NmgzNDEuMzMzMzM0VjIxMy4zMzMzMzNoODUuMzMzMzMzdjI5OC42NjY2NjdhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMS00Mi42NjY2NjcgNDIuNjY2NjY3SDI5OC42NjY2NjdhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMS00Mi42NjY2NjctNDIuNjY2NjY3VjIxMy4zMzMzMzNoODUuMzMzMzMzek0yNTYgMjEzLjMzMzMzM2g4NS4zMzMzMzMtODUuMzMzMzMzeiBtNDI2LjY2NjY2NyAwaDg1LjMzMzMzMy04NS4zMzMzMzN6IG0wIDU5Ny4zMzMzMzR2LTEyOEgzNDEuMzMzMzMzdjEyOEgyNTZ2LTE3MC42NjY2NjdhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMSA0Mi42NjY2NjctNDIuNjY2NjY3aDQyNi42NjY2NjZhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMSA0Mi42NjY2NjcgNDIuNjY2NjY3djE3MC42NjY2NjdoLTg1LjMzMzMzM3ogbTg1LjMzMzMzMyAwaC04NS4zMzMzMzMgODUuMzMzMzMzek0zNDEuMzMzMzMzIDgxMC42NjY2NjdIMjU2aDg1LjMzMzMzM3oiIHAtaWQ9IjI2NzkiIGZpbGw9IiMyYzJjMmMiPjwvcGF0aD48L3N2Zz4='
                // var previewEl = document.createElement('img')
                // previewEl.src = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/PjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+PHN2ZyB0PSIxNjIxMzI4NTkxMjQzIiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjU2NjMiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+PGRlZnM+PHN0eWxlIHR5cGU9InRleHQvY3NzIj48L3N0eWxlPjwvZGVmcz48cGF0aCBkPSJNNTEyIDE4Ny45MDRhNDM1LjM5MiA0MzUuMzkyIDAgMCAwLTQxOC41NiAzMTUuNjQ4IDQzNS4zMjggNDM1LjMyOCAwIDAgMCA4MzcuMTIgMEE0MzUuNDU2IDQzNS40NTYgMCAwIDAgNTEyIDE4Ny45MDR6TTUxMiAzMjBhMTkyIDE5MiAwIDEgMSAwIDM4NCAxOTIgMTkyIDAgMCAxIDAtMzg0eiBtMCA3Ni44YTExNS4yIDExNS4yIDAgMSAwIDAgMjMwLjQgMTE1LjIgMTE1LjIgMCAwIDAgMC0yMzAuNHpNMTQuMDggNTAzLjQ4OEwxOC41NiA0ODUuNzZsNC44NjQtMTYuMzg0IDQuOTI4LTE0Ljg0OCA4LjA2NC0yMS41NjggNC4wMzItOS43OTIgNC43MzYtMTAuODggOS4zNDQtMTkuNDU2IDEwLjc1Mi0yMC4wOTYgMTIuNjA4LTIxLjMxMkE1MTEuNjE2IDUxMS42MTYgMCAwIDEgNTEyIDExMS4xMDRhNTExLjQ4OCA1MTEuNDg4IDAgMCAxIDQyNC41MTIgMjI1LjY2NGwxMC4yNCAxNS42OGMxMS45MDQgMTkuMiAyMi41OTIgMzkuMTA0IDMyIDU5Ljc3NmwxMC40OTYgMjQuOTYgNC44NjQgMTMuMTg0IDYuNCAxOC45NDQgNC40MTYgMTQuODQ4IDQuOTkyIDE5LjM5Mi0zLjIgMTIuODY0LTMuNTg0IDEyLjgtNi40IDIwLjA5Ni00LjQ4IDEyLjYwOC00Ljk5MiAxMi45MjhhNTExLjM2IDUxMS4zNiAwIDAgMS0xNy4yOCAzOC40bC0xMi4wMzIgMjIuNC0xMS45NjggMjAuMDk2QTUxMS41NTIgNTExLjU1MiAwIDAgMSA1MTIgODk2YTUxMS40ODggNTExLjQ4OCAwIDAgMS00MjQuNDQ4LTIyNS42bC0xMS4zMjgtMTcuNTM2YTUxMS4yMzIgNTExLjIzMiAwIDAgMS0xOS44NC0zNS4wMDhMNTMuMzc2IDYxMS44NGwtOC42NC0xOC4yNC0xMC4xMTItMjQuMTI4LTcuMTY4LTE5LjY0OC04LjMyLTI2LjYyNC0yLjYyNC05Ljc5Mi0yLjQ5Ni05LjkyeiIgcC1pZD0iNTY2NCI+PC9wYXRoPjwvc3ZnPg=='
                // previewEl.width = 16
                // previewEl.height = 16
                var data_set = [{"name":"Sheet1","freeze":"A1","styles":[],"merges":[],
                        "rows":{
                            "0":{"cells":{"0":{"text":"id"},"1":{"text":"name"}}},
                            "1":{"cells":{"0":{"text":"1"},"1":{"text":"Tom"}}},
                            "2":{"cells":{"0":{"text":"2"},"1":{"text":"Hall"}}},
                            "3":{"cells":{"0":{"text":"3"},"1":{"text":"Sure"}}},
                            "len":5},
                            "cols":{"len":6},
                            "validations":[],
                            "autofilter":{}}]
                var htmlout = document.getElementById('x-spreadsheet-demo')
                var xs = x_spreadsheet(htmlout ,{
                    showToolbar: true,
                    showGrid: true,
                    showBottomBar: true,
                    extendToolbar: {
                      left: [
                        {
                          tip: 'Save',
                          icon: saveIcon,
                          onClick: (data, sheet) => {
                            console.log('click save button:', data, sheet)
                            self.do_action({
                                name: '统计',
                                type: 'ir.actions.act_window',
                                res_model: 'zy.statistics', // Module name goes here
                                view_mode: 'form',
                                view_type: 'form',
                                target: 'current',
                                res_id: data_other.id,
                                views: [[false, 'form']]
                              });
                          }
                        }
                      ],
                      right: [
                        {
                          tip: 'Preview',
                          el: saveIcon,
                          onClick: (data, sheet) => {
                            console.log('click preview button:', data)
                          }
                        }
                      ],
                    }
                  });
                xs.loadData(data_set)
                
            });
        }
    })
 
    core.action_registry.add('x_spreadsheet', spreadsheet);
    return spreadsheet;
})