// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Events and Programs", {
	refresh(frm) {
        if (frm.doc.event_status) {
            const status_colors = {
                "Live Event": "green",
                "Event Expired": "red",
                "Upcoming Event": "yellow"
            };
            const color = status_colors[frm.doc.event_status] || "gray";
            frm.page.set_indicator(__(frm.doc.event_status), color);
        }
        // on load, ensure group_ministry is hidden unless box is checked
        frm.toggle_display('group_ministry', !!frm.doc.specific_group_ministry);
    },
    specific_group_ministry(frm) {
        // when the checkbox is toggled
        frm.toggle_display('group_ministry', !!frm.doc.specific_group_ministry);
    }
});
