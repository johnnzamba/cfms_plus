# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CollectionTool(Document):
	pass


import json
import frappe

@frappe.whitelist()
def create_collections(church_branch, collection_date, service_type, general, specific):
    # Ensure general is a list of dictionaries
    if isinstance(general, str):
        general = json.loads(general)
    else:
        general = general or []

    # Ensure specific is a list of dictionaries
    if isinstance(specific, str):
        specific = json.loads(specific)
    else:
        specific = specific or []

    created_docs = []

    # Process general collections
    for row in general:
        amount = row.get('amount_received', 0)
        if amount > 0:
            # Example: Create a document (customize as needed)
            doc = frappe.get_doc({
                'doctype': 'Church Collections',
                'branch': church_branch,
                'non_detailed': 1,  # Flag for general collections
                'collection_type': row.get('collection_type'),
                'collection_date': collection_date,
                'church_service': service_type,
                'collection_received': amount,
                'amount_in_words': frappe.utils.money_in_words(amount)
            })
            doc.insert()
            created_docs.append(doc.name)

    # Process specific collections
    for row in specific:
        amount = row.get('amount_received', 0)
        if amount > 0:
            doc = frappe.get_doc({
                'doctype': 'Church Collections',
                'branch': church_branch,
                'is_specific': 1,  # Flag for specific collections
                'collection_type': row.get('collection_type'),
                'for_member': row.get('church_member'),
                'collection_date': collection_date,
                'church_service': service_type,
                'collection_received': amount,
                'amount_in_words': frappe.utils.money_in_words(amount)
            })
            doc.insert()
            created_docs.append(doc.name)

    return created_docs