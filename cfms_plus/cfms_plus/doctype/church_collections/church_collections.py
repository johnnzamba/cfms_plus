# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ChurchCollections(Document):
	pass

import frappe
import re
from frappe.utils import flt, nowdate


def create_journal_entry(doc=None, method=None, doc_name=None):
    """
    Hook on submit of Church Collections doctype to create a Journal Entry.
    """
    # Load the Church Collections document if doc not passed in
    if not doc and doc_name:
        doc = frappe.get_doc('Church Collections', doc_name)

    # 1. Extract and sanitize collection_received amount
    raw_amount = doc.collection_received
    cleaned = re.sub(r"[^0-9.\-]", "", str(raw_amount) or "")
    amount = flt(cleaned)
    if amount <= 0:
        frappe.throw(f"Invalid collection amount ({raw_amount}). Parsed as {amount}. Must be > 0.")

    # 2. Fetch default company and abbreviation
    default_company = frappe.get_value('Global Defaults', None, 'default_company')
    if not default_company:
        frappe.throw('Set a default company in Global Defaults.')
    abbr = frappe.get_value('Company', default_company, 'abbr') or ''

    # 3. Fetch branch code
    branch_code = frappe.get_value('Church Branch', doc.branch, 'branch_code') or ''

    # 4. Determine accounts
    mop = doc.mode_of_payment
    if mop == 'Cash':
        paid_from_account = f"Cash - {abbr}"
    elif mop == 'MPESA':
        paid_from_account = f"MPESA - {abbr}"
    else:
        paid_from_account = f"Bank Account - {abbr}"

    paid_to_account = f"{doc.collection_type} | {branch_code} - {abbr}"

    # 5. Prepare Journal Entry
    je = frappe.new_doc('Journal Entry')
    je.voucher_type = 'Journal Entry'
    je.is_system_generated = 1
    je.company = default_company
    je.posting_date = doc.collection_date or nowdate()
    je.custom_linked_to_collection = doc.name
    je.custom_journal_for_church_member = doc.for_member
    je.mode_of_payment = mop

    # 6. Append accounts using currency fields
    je.append('accounts', {
        'account': paid_from_account,
        'debit_in_account_currency': amount
    })
    je.append('accounts', {
        'account': paid_to_account,
        'credit_in_account_currency': amount
    })

    # 7. Insert and submit
    je.insert(ignore_permissions=True)
    je.submit()
    frappe.db.commit()

    # 8. Update original Church Collections doc
    # Mark journal created and store the JE name
    doc.db_set('journal_created', 1, update_modified=False)
    doc.db_set('journal_entry', je.name, update_modified=False)

    frappe.msgprint(f"Journal Entry {je.name} created for Church Collection {doc.name}.")




def update_member(doc=None, method=None, doc_name=None):
    """
    Hook on insert of a new Church Collections doc to link transaction to member and send acknowledgment.
    """
    if not doc and doc_name:
        doc = frappe.get_doc('Church Collections', doc_name)

    member_name = doc.for_member
    if not member_name:
        return

    try:
        # 1. Append to member's linked_transactions
        member = frappe.get_doc('Church Members', member_name)
        member.append('linked_transactions', {
            'collection_type': doc.collection_type,
            'collection_doc': doc.name,
            'transaction_date': doc.collection_date,
            'transaction_amount': doc.collection_received
        })
        member.save(ignore_permissions=True)
        frappe.db.commit()

        # 2. Send email acknowledgment using existing Email Template
        recipient = member.member_email
        if recipient:
            # Dynamic context for template
            args = {
                'full_name': member.full_name,
                'member_branch': member.branch,
                'collection_type': doc.collection_type,
                'collection_received': doc.collection_received
            }
            # Generate PDF attachment of the Church Collection
            pdf_data = frappe.get_print(
                'Church Collections',
                doc.name,
                print_format=None,
                as_pdf=True
            )
            attachment = {
                'fname': f"ChurchCollection_{doc.name}.pdf",
                'fcontent': pdf_data,
                'content_type': 'application/pdf'
            }
            # Queue the email using the template
            frappe.sendmail(
                recipients=[recipient],
                template='Church Members Giving Acknowledgement',
                args=args,
                attachments=[attachment],
                reference_doctype='Church Collections',
                reference_name=doc.name,
                delayed=True
            )
            frappe.msgprint(f"Acknowledgement email queued to {recipient} for {doc.name}.")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in update_member hook")
        frappe.msgprint(f"Failed to link/send acknowledgment: {str(e)}")
