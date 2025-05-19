// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt

let original_attendance_rows = [];
frappe.ui.form.on("Event or Program Attendance TOOL", {
    setup(frm) {
        frm.set_query("event_program_name", () => {
            return {
                filters: {
                    event_status: ["!=", "Event Expired"]
                }
            };
        });
    },
    refresh(frm) {
        frm.set_value("event_program_name", "");
        frm.set_value("event_branch", "");
        frm.set_value("event_date", "");
        frm.clear_table("attendance");
        frm.set_value("attendance_marked", 0);
        frm.refresh_field("attendance");
        // Disable the default Save button since it's a single doctype
        frm.disable_save();
        
        // Add custom Save Attendance button
        frm.add_custom_button(__("Save Attendance"), function() {
            frappe.dom.freeze(__("Marking Attendance..."));
        
            let doc_data = {
                event_program_name: frm.doc.event_program_name,
                event_branch: frm.doc.event_branch,
                event_date: frm.doc.event_date,
                attendance_marked: frm.doc.attendance_marked,
                attendance: frm.doc.attendance.map(row => ({
                    member_name: row.member_name,
                    event_date: row.event_date,
                    member_attended: row.member_attended
                }))
            };
        
            frappe.call({
                method: "cfms_plus.cfms_plus.doctype.event_or_program_attendance_tool.event_or_program_attendance_tool.mark_event_attendance",
                args: { doc_data: JSON.stringify(doc_data) },
                callback: function(r) {
                    frappe.dom.unfreeze();
        
                    if (r.message && r.message.status === "success") {
                        frappe.msgprint({
                            title: __("Success"),
                            message: __("Attendance recorded for {0} attendees.", [r.message.processed]),
                            indicator: "green"
                        });
                        frappe.utils.clear_cache();
        
                        frappe.model.with_doc("Event or Program Attendance TOOL", function() {
                            frappe.call({
                                method: "frappe.client.get",
                                args: {
                                    doctype: "Event or Program Attendance TOOL",
                                    name: "Event or Program Attendance TOOL"
                                },
                                callback: function(response) {
                                    if (response.message) {
                                        frm.doc = response.message;
                                        frm.doc.attendance = [];
                                        frm.set_value("event_program_name", "");
                                        frm.set_value("event_branch", "");
                                        frm.set_value("event_date", "");
                                        frm.set_value("attendance_marked", 0);
                                        frm.dirty_flag = false;
                                        frm.refresh();
                                        frm.refresh_field("attendance");
                                    }
                                }
                            });
                        });
                    } else if (r.message && r.message.status === "already marked") {
                        frappe.msgprint({
                            title: __("Info"),
                            message: __("Attendance has already been marked. Please REFRESH page!"),
                            indicator: "blue"
                        });
                    } else if (r.message && r.message.status === "no attendance marked") {
                        frappe.msgprint({
                            title: __("Warning"),
                            message: __("No attendees CHECKED PRESENT!"),
                            indicator: "orange"
                        });
                    } else {
                        frappe.msgprint({
                            title: __("Error"),
                            message: __("Failed to mark attendance. Check the error log."),
                            indicator: "red"
                        });
                    }
                },
                error: function(error) {
                    frappe.dom.unfreeze();
                    frappe.msgprint({
                        title: __("Error"),
                        message: __("Failed to mark attendance: ") + (error.message || "Unknown error"),
                        indicator: "red"
                    });
                }
            });
        }).css({
            "color": "white",
            "background-color": "#14141f", 
            "font-weight": "600"
        });        
    },
    event_date(frm) {
        if (frm.doc.attendance && frm.doc.event_date) {
            const selected_date = frm.doc.event_date;
            frm.doc.attendance.forEach(row => {
                row.event_date = selected_date;
            });    
            original_attendance_rows = frm.doc.attendance.map(r => ({
                member_name: r.member_name,
                event_date: selected_date,
                member_attended: r.member_attended
            }));
    
            frm.refresh_field("attendance");
        }
    },
    filter_member(frm) {
        const keyword = (frm.doc.filter_member || "").trim().toLowerCase();
        const selected_date = frm.doc.event_date;
    
        if (!original_attendance_rows.length) {
            original_attendance_rows = frm.doc.attendance.map(r => ({
                member_name: r.member_name,
                event_date: r.event_date,
                member_attended: r.member_attended
            }));
        }
    
        frm.clear_table("attendance");
    
        const rows_to_display = keyword
            ? original_attendance_rows.filter(row =>
                row.member_name.toLowerCase().includes(keyword)
            )
            : original_attendance_rows;
    
        rows_to_display.forEach(data => {
            const row = frm.add_child("attendance");
            row.member_name = data.member_name;
            row.member_attended = data.member_attended;
            row.event_date = selected_date;
        });
    
        frm.refresh_field("attendance");
    },
    mark_all(frm) {
        if (frm.doc.attendance && frm.doc.attendance.length > 0) {
            frm.doc.attendance.forEach(row => {
                row.member_attended = 1;
            });
            frm.refresh_field("attendance");
        }
    },
    event_program_name(frm) {
      if (!frm.doc.event_program_name) {
        return;
      }
  
      // 1) Fetch branch & dates for the selected event
      frappe.call({
        method: "cfms_plus.cfms_plus.doctype.event_or_program_attendance_tool.event_or_program_attendance_tool.get_event_branch_and_dates",
        args: { event_name: frm.doc.event_program_name },
        callback: (r) => {
          if (r.message) {
            const { church_branch, event_from, end_date } = r.message;
  
            // 2) Prefill the branch
            frm.set_value("event_branch", church_branch);
  
            // 3) Build the date options
            let start = frappe.datetime.str_to_obj(event_from);
            const end   = frappe.datetime.str_to_obj(end_date);
            const options = [];
            while (start <= end) {
              options.push(frappe.datetime.obj_to_str(start));
              // advance one day
              start.setDate(start.getDate() + 1);
            }
  
            // 4) Set the select options on event_date
            frm.set_df_property("event_date", "options", [""].concat(options));
            frm.refresh_field("event_date");
  
            // 5) Fetch branch members
            frappe.call({
              method: "cfms_plus.cfms_plus.doctype.event_or_program_attendance_tool.event_or_program_attendance_tool.get_branch_members",
              args: { branch: church_branch },
              callback: (r2) => {
                if (r2.message && Array.isArray(r2.message)) {
                  // clear existing table
                  frm.clear_table("attendance");
  
                  // populate rows
                  r2.message.forEach(member_name => {
                    const row = frm.add_child("attendance");
                    row.member_name     = member_name;
                    row.event_date = frm.doc.event_date;
                    row.member_attended = 0;
                  });
  
                  frm.refresh_field("attendance");
                  original_attendance_rows = frm.doc.attendance.map(r => ({
                    member_name: r.member_name,
                    event_date: r.event_date,
                    member_attended: r.member_attended
                  }));
                  
                  // show the Mark All button
                  frm.toggle_display("mark_all", true);
                  frm.toggle_display("filter_member", true);
                }
              }
            });
          }
        }
      });
    }
});