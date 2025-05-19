# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class QuestionnaireforEventsandPrograms(Document):
	pass


import frappe
from frappe import _
from frappe.utils import formatdate

@frappe.whitelist()
def save_attendance(doc=None, method=None, doc_name=None):
    """
    after_insert hook on Questionnaire for Events and Programs.
    Also callable as API with doc_name for testing.
    """
    # 1) Load the Questionnaire doc if called via doc_name
    if doc_name:
        doc = frappe.get_doc("Questionnaire for Events and Programs", doc_name)

    # Required fields on doc: full_name, event_program (Link), gender, date
    event_program = doc.event_program
    attendee_name = doc.full_name
    attended_on = doc.date
    gender = doc.gender

    # 2) Load the Church Event by its program name
    ev = frappe.get_all("Church Events and Programs",
                        filters={"event_program_name": event_program},
                        limit_page_length=1, fields=["name"])[0]
    event_doc = frappe.get_doc("Church Events and Programs", ev.name)

    # 3) Append to its event_program_attendance table
    event_doc.append("event_program_attendance", {
        "member":      attendee_name,
        "attended_on": attended_on,
        "is_present":  1
    })

    # 4) Recompute totals by gender from all Questionnaires for this event
    counts = {}
    for g in ("Male", "Female", "Other"):
        counts[g] = frappe.db.count(
            "Questionnaire for Events and Programs",
            {"event_program": event_program, "gender": g}
        )

    total_str = _("{m} Male | {f} Female | {o} Other").format(
        m=counts["Male"], f=counts["Female"], o=counts["Other"]
    )
    event_doc.total_attendees = total_str

    # 5) Save the Church Events doc
    event_doc.save(ignore_permissions=True)
    frappe.db.commit()

    # 6) Find the Church Member by full_name and append linked_events
    members = frappe.get_all("Church Members",
                             filters={"full_name": attendee_name},
                             limit_page_length=1,
                             fields=["name"])
    if members:
        member_doc = frappe.get_doc("Church Members", members[0].name)
        member_doc.append("linked_events", {
            "event":       event_program,
            "attended_on": attended_on
        })
        member_doc.save(ignore_permissions=True)
        frappe.db.commit()

    return {"status":"success", "event": ev.name, "member": attendee_name}
