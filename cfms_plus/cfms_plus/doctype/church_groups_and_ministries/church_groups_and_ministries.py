# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ChurchGroupsandMinistries(Document):
	def autoname(self):
		"""
		Generate unique name based on group_ministry_name and either branch_code or ministry code.
		"""
		if not self.group_ministry_name:
			frappe.throw(_("Group/Ministry Name is required."))

		base = self.group_ministry_name.strip()

		# If branch-specific, append branch_code
		if self.is_branch_specific:
			if not self.applicable_branch:
				frappe.throw(_("Applicable Branch is required when branch-specific."))

			branch = frappe.get_doc('Church Branch', self.applicable_branch)
			if not branch.branch_code:
				frappe.throw(_("Selected branch has no branch_code."))

			base = f"{base} - {branch.branch_code.strip()}"
		# Fallback to group_ministry_code if provided
		elif self.group_ministry_code:
			base = f"{base} - {self.group_ministry_code.strip()}"

		# Set the doc name
		self.name = base
		self.group_ministry_name = base

