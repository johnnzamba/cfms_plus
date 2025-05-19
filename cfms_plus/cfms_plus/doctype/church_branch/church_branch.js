// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Branch", {
	refresh(frm) {
        frm.set_query("parent_church_branch", function() {
            return {
                filters: {
                    is_group: 1
                }
            };
        });
        toggle_field_visibility(frm);
	},
    parent_church_branch(frm) {
        toggle_field_visibility(frm);
    },

    is_group(frm) {
        toggle_field_visibility(frm);
    }
});
function toggle_field_visibility(frm) {
    frm.toggle_display("is_group", !frm.doc.parent_church_branch);
    frm.toggle_display("parent_church_branch", !frm.doc.is_group);
}