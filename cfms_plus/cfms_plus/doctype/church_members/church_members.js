// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Members", {
	refresh(frm) {
        // Status indicator
        if (frm.doc.membership_status) {
            const status_colors = {
                "Active": "green",
                "Inactive": "orange",
                "Moved Out": "red",
                "Deceased": "yellow"
            };
            const color = status_colors[frm.doc.membership_status] || "gray";
            frm.page.set_indicator(__(frm.doc.membership_status), color);
        }

        // Build transaction graph if there are linked transactions
        const transactions = frm.doc.linked_transactions || [];
        if (transactions.length) {
            const labels = [];
            const values = [];
            const docLabels = [];

            transactions.forEach(row => {
                labels.push(frappe.datetime.str_to_obj(row.transaction_date).toISOString().substr(0,10));
                values.push(row.transaction_amount);
                docLabels.push(row.collection_doc);
            });

            if (!frm.fields_dict.transaction_graph) return;
            frm.fields_dict.transaction_graph.$wrapper.empty();

            const chartDiv = $("<div style='height:300px;'></div>").appendTo(frm.fields_dict.transaction_graph.$wrapper);

            new frappe.Chart(chartDiv[0], {
                data: { labels: labels, datasets: [{ name: __("Amount"), values: values }] },
                type: 'bar',
                height: 300,
                colors: ['#3498db'],
                axisOptions: { xIsSeries: true },
                tooltipOptions: {
                    formatTooltipX: label => {
                        // label is date string
                        const idx = labels.indexOf(label);
                        return `<b>${docLabels[idx]}</b><br>${label}`;
                    },
                    // Y tooltip remains amount
                    formatTooltipY: value => value
                }
            });
        }
    }
});
