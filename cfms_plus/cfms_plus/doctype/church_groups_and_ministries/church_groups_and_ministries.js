// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Groups and Ministries", {
	refresh(frm) {
		frm.toggle_display('applicable_branch', frm.doc.is_branch_specific);
		frm.toggle_display('under_group_ministry', !frm.doc.is_group);
		frm.toggle_display('collection_acc', frm.doc.has_collection_acc);
		frm.trigger('filter_collection_acc');
        if (frm.doc.group_ministry_status) {
            const status_colors = {
                "Active": "green",
                "Inactive": "red",
                "Passive": "orange",
                "Under Formation": "yellow"
            };
            const color = status_colors[frm.doc.group_ministry_status] || "gray";
            frm.page.set_indicator(__(frm.doc.group_ministry_status), color);
        }
	},

	under_group_ministry(frm) {
		if (frm.doc.under_group_ministry) {
			frm.set_value('is_group', 0);
			frm.toggle_display('is_group', false);
		} else {
			frm.toggle_display('is_group', true);
		}
	},

	applicable_branch(frm) {
		frm.trigger('filter_collection_acc');
	},

	filter_collection_acc(frm) {
		if (!frm.doc.applicable_branch) {
			frm.set_query("collection_acc", () => {
				return {
					filters: {
						name: ["=", ""],
					}
				};
			});
			return;
		}

		// Fetch branch_code from the selected Church Branch
		frappe.db.get_value("Church Branch", frm.doc.applicable_branch, "branch_code")
			.then(r => {
				if (!r || !r.message || !r.message.branch_code) return;

				const branch_code = r.message.branch_code;

				frm.set_query("collection_acc", () => {
					return {
						filters: [
							["Account", "name", "like", `%${branch_code}%`]
						]
					};
				});
			});
	},

	is_branch_specific(frm)  { frm.trigger('refresh'); },
	is_group(frm)            { frm.trigger('refresh'); },
	has_collection_acc(frm)  { frm.trigger('refresh'); }
});
