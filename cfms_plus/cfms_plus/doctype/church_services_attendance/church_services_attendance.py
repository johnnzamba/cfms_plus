# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _
from frappe.model.document import Document


class ChurchServicesAttendance(Document):
	def validate(self):
        # Only on new documents (not on update)
		if self.is_new():
			exists = frappe.db.exists({
				"doctype": "Church Services Attendance",
				"service_date": self.service_date
			})
			if exists:
				# pass the bolded date as the second argument to _()
				frappe.throw(
					_("An attendance record for {0} already exists.", frappe.bold(self.service_date)),
					title=_("Duplicate Date"),
					exc=frappe.DuplicateEntryError
				)

@frappe.whitelist()
def get_branch_members(branch):
	"""
	Returns a list of names of Church Members whose member_branch equals the given branch.
	Called from client side when a branch is selected.
	"""
	if not branch:
		frappe.throw(_("Branch not provided"), exc=frappe.ValidationError)

	members = frappe.get_all(
		"Church Members",
		filters={"member_branch": branch},
		fields=["name"],
		order_by="name"
	)
	return [m.name for m in members]

import frappe

@frappe.whitelist()
def update_member_attendance(doc=None, method=None, doc_name=None):
    """
    On submit of Church Services Attendance, mark all selected members as present
    and append a record to each Member's linked_service table.
    """
    if doc_name and not doc:
        doc = frappe.get_doc("Church Services Attendance", doc_name)

    # Filter rows with is_present == 1
    present_rows = [r for r in doc.members_table if r.is_present]
    if not present_rows:
        return

    for row in present_rows:
        # Load the Church Member document
        member_doc = frappe.get_doc("Church Members", row.member)

        # Append to its linked_service child table
        member_doc.append("linked_service", {
            "service": doc.service_type,
            "attended_on": doc.service_date,
            "attended": 1
        })
        member_doc.save()

    frappe.db.commit()