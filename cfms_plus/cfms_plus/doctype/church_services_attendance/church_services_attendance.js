// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt
frappe.ui.form.on("Church Services Attendance", {
    setup(frm) {
        // Filter the Link field “service_type”
        frm.set_query("service_type", () => {
            if (!frm.doc.service_date) return {};
            const weekday = frappe.datetime
                .str_to_obj(frm.doc.service_date)
                .toLocaleDateString("en-US", { weekday: "long" });
            return {
                filters: { name: ["like", `%${weekday}%`] }
            };
        });
    },

    refresh(frm) {
        // 1) Inject a non‑closable intro banner
        frm.set_intro(`
            <div class="attendance-alert">
                ${__("Ensure document is Submitted for Attendance to be properly recorded!")}
            </div>
        `);

        // 2) Immediately strip out the close icon and adjust spacing
        const intro = frm.wrapper.find(".form-intro");
        intro.find(".close").remove();
        intro.css({
            "margin-bottom": "1.5rem",   // push the form down a bit
            "padding": "0.75rem 1rem",    // tighten the padding
            "background": "#e7f1ff",      // light blue
            "border": "1px solid #c6def7",
            "color": "#31708f"
        });

        // 3) Show/hide your Mark All button based on members_table
        frm.toggle_display('mark_all', !!(frm.doc.members_table || []).length);

        // 4) Render those head‑count icons
        render_counts(frm);
    },

    service_date(frm) {
        // 1) Clear service_type for re‑filter
        frm.set_value("service_type", "");
        frm.refresh_field("service_type");

        // 2) If a date is selected, check for duplicates
        if (frm.doc.service_date) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Church Services Attendance',
                    filters: { service_date: frm.doc.service_date },
                    fieldname: 'name'
                },
                callback: (r) => {
                    if (r.message && r.message.name) {
                        // Duplicate found!
                        frappe.msgprint({
                            title:  __("Duplicate Date"),
                            message: __("An attendance record for {0} already exists.", [frm.doc.service_date]),
                            indicator: 'red'
                        });
                        // clear the invalid selection
                        frm.set_value('service_date', '');
                        frm.refresh_field('service_date');
                    }
                }
            });
        }
    },

    church_branch(frm) {
        if (!frm.doc.church_branch) return;
        frappe.call({
            method: "cfms_plus.cfms_plus.doctype.church_services_attendance.church_services_attendance.get_branch_members",
            args: { branch: frm.doc.church_branch },
            callback: (r) => {
                if (Array.isArray(r.message)) {
                    frm.clear_table("members_table");
                    r.message.forEach(member_name => {
                        let row = frm.add_child("members_table");
                        row.member = member_name;
                        row.is_present = 0;
                    });
                    frm.refresh_field("members_table");

                    // show Mark All now that table is populated
                    frm.toggle_display('mark_all', true);
                }
            }
        });
    },

    mark_all(frm) {
        (frm.doc.members_table || []).forEach(row => row.is_present = 1);
        frm.refresh_field("members_table");
    },

    men_attendance(frm)      { render_counts(frm); },
    women_attendance(frm)    { render_counts(frm); },
    children_attendance(frm) { render_counts(frm); }
});


// ————————————————
// Helpers
// ————————————————

/**
 * Render the men/women/children counts with icons in the HTML field
 */
function render_counts(frm) {
    let m = frm.doc.men_attendance  || 0;
    let w = frm.doc.women_attendance|| 0;
    let c = frm.doc.children_attendance || 0;

    // Build each block
    let blocks = [];
    blocks.push(`
        <div style="text-align:center; margin-bottom:1rem">
            <img width="100" height="100" src="https://img.icons8.com/matisse/100/standing-man.png" alt="standing-man"/>
            <div style="font-weight:bold">${m}</div>
        </div>
    `);
    blocks.push(`
        <div style="text-align:center; margin-bottom:1rem">
            <img width="100" height="100"
                 src="https://img.icons8.com/matisse/100/standing-woman.png"
                 alt="woman"/>
            <div style="font-weight:bold">${w}</div>
        </div>
    `);
    blocks.push(`
        <div style="text-align:center;">
            <img width="100" height="100"
                 src="https://img.icons8.com/papercut/100/children.png"
                 alt="children"/>
            <div style="font-weight:bold">${c}</div>
        </div>
    `);

    // Inject into the HTML field
    frm.fields_dict.render_counts.$wrapper.html(blocks.join(""));
}

