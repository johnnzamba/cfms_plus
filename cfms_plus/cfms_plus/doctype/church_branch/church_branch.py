# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ChurchBranch(Document):
    def autoname(self):
        """Generate a unique name for the ChurchBranch document."""
        if not self.branch_name:
            frappe.throw(_("Branch Name is required."))
        if not self.branch_code:
            frappe.throw(_("Unique Branch Code is required."))        
        new_name = f"{self.branch_name.strip()} - {self.branch_code.strip()}"
        self.name = new_name        
        self.branch_name = new_name

import frappe


def create_coa(doc, method):
    """
    After inserting a Church Branch, create Chart of Accounts entries for
    Trust Funds and Local Church Funds, plus child accounts for each Collection Type.
    """
    # Fetch all Collection Type records
    collections = frappe.get_all(
        "Collection Type",
        fields=["name", "collection_type"]
    )

    # Get default company from Global Defaults
    gd = frappe.get_single("Global Defaults")
    default_company = gd.default_company

    # Get company abbreviation
    company_doc = frappe.get_doc("Company", default_company)
    abbr = company_doc.abbr

    # Extract branch_code from the new Church Branch
    branch_code = doc.branch_code
    branch_name = doc.name

    # Define parent group specifications
    parent_specs = [
        {"type": "Trust Funds", "title": "Trust Funds | {code}"},
        {"type": "Local Church Funds", "title": "Local Church Funds | {code}"}
    ]

    # Create or fetch both parent groups under "Income - {abbr}" first
    parent_map = {}
    root_parent = f"Income - {abbr}"

    for spec in parent_specs:
        acct_name = spec["title"].format(code=branch_code)
        existing = frappe.db.get_value(
            "Account",
            {"account_name": acct_name, "company": default_company},
            "name"
        )
        if existing:
            parent_map[spec["type"]] = existing
        else:
            new_parent = frappe.get_doc({
                "doctype": "Account",
                "account_name": acct_name,
                "company": default_company,
                "is_group": 1,
                "custom_church_branch": branch_name,
                "root_type": "Income",
                "parent_account": root_parent,
            })
            new_parent.insert(ignore_permissions=True)
            frappe.db.commit()
            parent_map[spec["type"]] = new_parent.name

    # Now that both parent groups exist, create child accounts
    for c in collections:
        name = c.get("name")
        c_type = c.get("collection_type")

        if c_type not in parent_map:
            continue

        parent_acct = parent_map[c_type]
        child_name = f"{name} | {branch_code}"

        if not frappe.db.exists("Account", {"account_name": child_name, "company": default_company}):
            child = frappe.get_doc({
                "doctype": "Account",
                "account_name": child_name,
                "company": default_company,
                "is_group": 0,
                "custom_church_branch": branch_name,
                "root_type": "Income",
                "parent_account": parent_acct,
            })
            child.insert(ignore_permissions=True)
            frappe.db.commit()

    frappe.msgprint(f"Trust Funds and Local Church Funds accounts created successfully for branch {branch_code}.")
    frappe.db.set_value(
        "Church Branch",
        doc.name,
        "branch_accounts_created",
        1
    )
    frappe.db.commit()