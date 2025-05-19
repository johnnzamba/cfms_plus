# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CollectionType(Document):
    def autoname(self):
        """Generate a unique name for the CollectionType document."""
        # Validate required fields
        if not self.collection_name:
            frappe.throw(_("Collection Name is required."))
        
        if not self.collection_code:
            frappe.throw(_("Unique Collection Code is required."))
        
        # Generate custom name by combining collection_name and collection_code
        new_name = f"{self.collection_name.strip()} - {self.collection_code.strip()}"
        self.name = new_name
        
        # Sync collection_name with the generated name
        self.collection_name = new_name