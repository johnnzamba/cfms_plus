# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EventorProgramAttendanceTOOL(Document):
	pass

@frappe.whitelist()
def get_event_branch_and_dates(event_name):
    """
    Return church_branch, event_from, end_date for the given event.
    """
    ev = frappe.get_doc("Church Events and Programs", event_name)
    return {
        "church_branch": ev.church_branch,
        "event_from":    ev.event_from,
        "end_date":      ev.end_date
    }

@frappe.whitelist()
def get_branch_members(branch):
    """
    Return a list of Church Member.names for the given branch.
    """
    members = frappe.get_all("Church Members",
                             filters={"member_branch": branch},
                             fields=["name"])
    # extract just the name string
    return [m.name for m in members]

import frappe
from frappe import _
import json

@frappe.whitelist()
def mark_event_attendance(doc_data):
    try:
        # Parse the JSON string into a Python dictionary
        doc_data = json.loads(doc_data)
        
        # Fetch the singleton instance of the single doctype
        doc = frappe.get_single("Event or Program Attendance TOOL")
        
        # Update fields from doc_data, excluding system fields and child table
        for field, value in doc_data.items():
            if field not in ["name", "doctype", "attendance"]:
                doc.set(field, value)
        
        # Handle the attendance child table
        if "attendance" in doc_data:
            doc.attendance = []  # Clear existing rows
            for row in doc_data["attendance"]:
                doc.append("attendance", {
                    "member_name": row.get("member_name"),
                    "event_date": row.get("event_date"),
                    "member_attended": row.get("member_attended", 0)
                })
        
        # Check if attendance is already marked
        if doc.attendance_marked == 1:
            return {"status": "already marked"}
        
        # Save the document
        doc.save(ignore_permissions=True)
        
        # Extract event and attendance details
        event_name = doc.event_program_name
        attendance_rows = [r for r in doc.attendance if r.member_attended == 1]

        # If no event or attendees, update status and exit
        if not event_name or not attendance_rows:
            doc.attendance_marked = 0
            doc.save(ignore_permissions=True)
            return {"status": "no attendance marked"}

        # Update the Church Event document
        event_doc = frappe.get_doc("Church Events and Programs", event_name)
        for row in attendance_rows:
            event_doc.append("event_program_attendance", {
                "member": row.member_name,
                "attended_on": row.event_date,
                "is_present": 1
            })

        # Calculate total attendees by gender
        gender_counts = {"Male": 0, "Female": 0, "Other": 0}
        for child in event_doc.event_program_attendance:
            if child.is_present:
                gender = frappe.get_value("Church Members", child.member, "member_gender") or "Other"
                gender_counts[gender] += 1

        event_doc.total_attendees = _("{m} Male | {f} Female | {o} Other").format(
            m=gender_counts["Male"],
            f=gender_counts["Female"],
            o=gender_counts["Other"]
        )
        event_doc.save(ignore_permissions=True)

        # Update Church Members with event attendance
        for row in attendance_rows:
            member = frappe.get_doc("Church Members", row.member_name)
            member.append("linked_events", {
                "event": event_name,
                "attended_on": row.event_date
            })
            member.save(ignore_permissions=True)

        # Mark attendance as processed
        doc.attendance_marked = 1
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "processed": len(attendance_rows)}

    except Exception as e:
        frappe.log_error(f"Attendance Marking Failed: {str(e)}", "Event Attendance Error")
        if 'doc' in locals():
            doc.attendance_marked = 0
            doc.save(ignore_permissions=True)
        frappe.db.commit()
        raise frappe.ValidationError(f"Failed to mark attendance: {str(e)}")