// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt

frappe.ui.form.on("Collection Tool", {
    setup(frm) {
        // Filter the Link field “service_type”
        frm.set_query("service_type", () => {
            if (!frm.doc.collection_date) return {};
            const weekday = frappe.datetime
                .str_to_obj(frm.doc.collection_date)
                .toLocaleDateString("en-US", { weekday: "long" });
            return {
                filters: { name: ["like", `%${weekday}%`] }
            };
        });
    },
	refresh(frm) {
        // Hide the church_member filter input initially (if applicable)
        frm.set_df_property('church_member', 'hidden', true);
        
        // Set custom primary button "Submit Collections"
        frm.page.set_primary_action(__('Submit Collections'), function() {
            // Fetch form data on the fly
            let args = {
                church_branch: frm.doc.church_branch,
                collection_date: frm.doc.collection_date,
                service_type: frm.doc.service_type,
                general: frm.doc.general || [],  // Default to empty array if not present
                specific: frm.doc.specific || [] // Default to empty array if not present
            };

            // Call the server-side method with freeze functionality
            frappe.call({
                method: 'cfms_plus.cfms_plus.doctype.collection_tool.collection_tool.create_collections',
                args: args,
                freeze: true,                  // Freeze the form during the call
                freeze_message: __('Recording Collections'),  // Display custom message
                callback: function(response) {
                    // Clear all form fields and child tables
                    frm.set_value('church_branch', null);
                    frm.set_value('collection_date', null);
                    frm.set_value('service_type', null);
                    frm.clear_table('general');
                    frm.clear_table('specific');
                    frm.refresh_field('general');
                    frm.refresh_field('specific');

                    // Show notification based on the response
                    if (response.message) {
                        if (response.message.length > 0) {
                            let doc_names = response.message.join(', ');
                            frappe.msgprint({
                                message: __('Created Church Collections: {0}', [doc_names]),
                                indicator: 'green',    // Green notification for success
                                title: __('Success')
                            });
                        } else {
                            frappe.msgprint({
                                message: __('No collections to submit.'),
                                indicator: 'green',    // Green notification (consistent styling)
                                title: __('Info')
                            });
                        }
                    }
                }
            });
        });
    },

	church_branch(frm) {
		if (!frm.doc.church_branch) return;

		// 1) Fetch and prefill the 'specific' table with Church Members filtered by branch
		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Church Members',
				fields: ['name'],
				filters: { member_branch: frm.doc.church_branch }
			},
			callback: function(r) {
				if (r.message) {
					// clear existing rows
					frm.clear_table('specific');
					// Populate table
					r.message.forEach(function(member) {
						let row = frm.add_child('specific');
						row.church_member = member.name;
					});
					frm.refresh_field('specific');

					// Show the filter input once the table is populated
					frm.set_df_property('church_member', 'hidden', false);

					// Attach live filter on the filter field
					let $filter = frm.get_field('church_member').$input;
					$filter.off('input.collection_filter').on('input.collection_filter', function() {
						let val = $(this).val().toLowerCase();
						// Iterate through each grid row for show/hide
						frm.fields_dict.specific.grid.grid_rows.forEach(function(grid_row) {
							let memberName = (grid_row.doc.church_member || '').toLowerCase();
							// Use grid_row.wrapper to show/hide the row DOM
							if (memberName.indexOf(val) !== -1) {
								grid_row.wrapper.show();
							} else {
								grid_row.wrapper.hide();
							}
						});
					});
				}
			}
		});

		// 2) Fetch and prefill the 'general' table with all Collection Types
		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Collection Type',
				fields: ['name']
			},
			callback: function(r) {
				if (r.message) {
					frm.clear_table('general');
					r.message.forEach(function(ct) {
						let row = frm.add_child('general');
						row.collection_type = ct.name;
					});
					frm.refresh_field('general');
				}
			}
		});
	},
    // collection_date(frm) {
    //     // 1) Clear service_type for re‑filter
    //     frm.set_value("service_type", "");
    //     frm.refresh_field("service_type");

    //     // 2) If a date is selected, check for duplicates
    //     if (frm.doc.collection_date) {
    //         frappe.call({
    //             method: 'frappe.client.get_value',
    //             args: {
    //                 doctype: 'Church Collections',
    //                 filters: { collection_date: frm.doc.collection_date },
    //                 fieldname: 'name'
    //             },
    //             callback: (r) => {
    //                 if (r.message && r.message.name) {
    //                     // Duplicate found!
    //                     frappe.msgprint({
    //                         title:  __("Duplicate Date"),
    //                         message: __("An attendance record for {0} already exists.", [frm.doc.collection_date]),
    //                         indicator: 'red'
    //                     });
    //                     // clear the invalid selection
    //                     frm.set_value('collection_date', '');
    //                     frm.refresh_field('collection_date');
    //                 }
    //             }
    //         });
    //     }
    // }
});
