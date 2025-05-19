# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChurchMembers(Document):
    def autoname(self):
        """
        Automatically set the document name as:
        {full_name} - {branch_code}
        """
        # Ensure full_name is present
        if not self.full_name:
            frappe.throw(_("Full Name is required to generate the document name."))

        # Clean up full name (remove leading/trailing whitespace)
        full_name_clean = self.full_name.strip()

        # Initialize branch_code
        branch_code = ""

        # Fetch branch_code if member_branch is set
        if self.member_branch:
            try:
                branch = frappe.get_doc("Church Branch", self.member_branch)
                branch_code = (branch.branch_code or "").strip()
            except frappe.DoesNotExistError:
                frappe.throw(_("Invalid member branch selected."))

        # Build the name string
        if branch_code:
            new_name = f"{full_name_clean} - {branch_code}"
        else:
            new_name = full_name_clean

        # Set the document name
        self.name = new_name

import frappe
from frappe import _

def generate_member_id(doc, method):
    """
    After inserting a Church Member, build and set member_id as:
      {INITIALS} - {BRANCH_CODE} - {SEQ:003}
    where SEQ is the 1-based count of members in that branch.
    """
    # 1) Compute initials from full_name
    name_parts = (doc.full_name or "").strip().split()
    if len(name_parts) > 1:
        initials = "".join([p[0].upper() for p in name_parts])
    else:
        initials = (name_parts[0][:2] if name_parts else "").upper()

    # 2) Fetch branch_code
    branch_code = ""
    if doc.member_branch:
        branch = frappe.get_doc("Church Branch", doc.member_branch)
        branch_code = (branch.branch_code or "").strip()

    # 3) Count existing members in this branch (including this new one)
    filters = {"member_branch": doc.member_branch} if doc.member_branch else {}
    total = frappe.db.count("Church Members", filters)

    # 4) Build sequence, zero-padded to 3 digits
    seq = str(total).zfill(3)

    # 5) Compose member_id
    member_id = f"{initials} - {branch_code} - {seq}"

    # 6) Update the record
    frappe.db.set_value("Church Members", doc.name, "member_id", member_id)
    frappe.db.commit()


import frappe
from frappe import _

@frappe.whitelist()
def register_member_to_group_ministry(member, group_ministry):
    """
    Register a member to a group/ministry, performing checks and updates as required.
    
    Args:
        member (str): Name of the Church Member
        group_ministry (str): Name of the Church Groups and Ministries
    """
    # Fetch the Church Member document
    member_doc = frappe.get_doc("Church Members", member)
    
    # Check 1: Is the member already linked to this group/ministry?
    for row in member_doc.linked_group_ministry:
        if row.group_ministry == group_ministry:
            frappe.msgprint(_("Member is already in the Group/Ministry {0}").format(group_ministry))
            return
    
    # Fetch the Church Groups and Ministries document
    group_doc = frappe.get_doc("Church Groups and Ministries", group_ministry)
    
    # Check 2: Is the member already in the group's member_breakdown?
    for row in group_doc.member_breakdown:
        if row.member == member:
            frappe.msgprint(_("Member is already registered in the Group/Ministry {0}").format(group_ministry))
            return
    
    # If both checks pass, proceed with updates
    
    # Update Church Member: Add row to linked_group_ministry
    member_doc.append("linked_group_ministry", {
        "group_ministry": group_ministry,
        "membership_started_on": frappe.utils.now()
    })
    
    # Get the member's gender
    gender = member_doc.member_gender or "Others" 
    
    # Update Church Groups and Ministries: Add row to member_breakdown
    group_doc.append("member_breakdown", {
        "member": member,
        "gender": gender,
        "joined_on": frappe.utils.now()
    })
    
    # Update member_count field
    member_count_str = group_doc.member_count or "0 Male | 0 Female | 0 Others"
    parts = member_count_str.split(" | ")
    counts = {}
    for part in parts:
        num, category = part.split(" ", 1)
        counts[category] = int(num)
    
    # Increment the count based on gender
    if gender in counts:
        counts[gender] += 1
    else:
        counts[gender] = 1
    
    # Reconstruct the member_count string
    new_parts = [f"{count} {category}" for category, count in counts.items()]
    group_doc.member_count = " | ".join(new_parts)
    
    # Save both documents
    member_doc.save()
    group_doc.save()
    frappe.db.commit()
    
    # Show success message
    frappe.msgprint(_("Member {0} successfully registered to Group/Ministry {1}").format(member, group_ministry))


import frappe
from frappe import _

@frappe.whitelist()
def check_member_in_group(member, group_ministry):
    """
    Check if a member is already associated with a group/ministry.

    Args:
        member (str): Name of the Church Member
        group_ministry (str): Name of the Church Groups and Ministries

    Returns:
        bool: True if the member is in the group/ministry, False otherwise
    """
    member_doc = frappe.get_doc("Church Members", member)
    for row in member_doc.linked_group_ministry:
        if row.group_ministry == group_ministry:
            return True
    return False

@frappe.whitelist()
def remove_member_from_group_ministry(member, group_ministry):
    """
    Remove a member from a group/ministry and update the member count.

    Args:
        member (str): Name of the Church Member
        group_ministry (str): Name of the Church Groups and Ministries
    """
    member_doc = frappe.get_doc("Church Members", member)
    group_doc = frappe.get_doc("Church Groups and Ministries", group_ministry)

    # Verify the member is in the group
    if not any(row.group_ministry == group_ministry for row in member_doc.linked_group_ministry):
        frappe.msgprint(_("Member {0} is not in Group/Ministry {1}").format(member, group_ministry))
        return

    # Remove the row from linked_group_ministry in Church Member
    member_doc.linked_group_ministry = [
        row for row in member_doc.linked_group_ministry
        if row.group_ministry != group_ministry
    ]

    # Remove the row from member_breakdown in Church Groups and Ministries
    group_doc.member_breakdown = [
        row for row in group_doc.member_breakdown
        if row.member != member
    ]

    # Update member_count based on gender
    gender = member_doc.member_gender or "Others"
    member_count_str = group_doc.member_count or "0 Male | 0 Female | 0 Others"
    parts = member_count_str.split(" | ")
    counts = {}
    for part in parts:
        num, category = part.split(" ", 1)
        counts[category] = int(num)

    # Decrement the appropriate gender count, ensuring it doesn't go below 0
    if gender in counts and counts[gender] > 0:
        counts[gender] -= 1

    # Reconstruct the member_count string
    group_doc.member_count = " | ".join([f"{count} {category}" for category, count in counts.items()])

    # Save changes to both documents
    member_doc.save()
    group_doc.save()
    frappe.db.commit()

    frappe.msgprint(_("Member {0} removed from Group/Ministry {1}").format(member, group_ministry))