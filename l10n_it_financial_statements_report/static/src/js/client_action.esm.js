/** @odoo-module **/
import {ReportAction} from "@web/webclient/actions/reports/report_action";
import {patch} from "web.utils";

patch(ReportAction.prototype, "l10n_it_financial_statements_report.ReportAction", {
    export() {
        this.action.doAction({
            type: "ir.actions.report",
            report_type: "xlsx",
            report_name: "l10n_it_financial_statements_report.report_xlsx",
            report_file: "l10n_it_financial_statements_report.report_xlsx",
            data: this.props.data || {},
            context: this.props.context || {},
            display_name: this.title,
        });
    },
});
