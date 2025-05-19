// Copyright (c) 2025, John Kitheka and contributors
// For license information, please see license.txt
frappe.ui.form.on("Church Collections", {
	refresh(frm) {
        // 1) If non_detailed is checked, hide the specific‑related fields
        if (frm.doc.non_detailed) {
          frm.set_df_property("is_specific", "hidden", true);
          frm.set_df_property("for_member",  "hidden", true);
          frm.set_df_property("msisdn",       "hidden", true);
        } else {
          frm.set_df_property("is_specific", "hidden", false);
          frm.set_df_property("for_member",  "hidden", false);
          frm.set_df_property("msisdn",       "hidden", false);
        }
    
        // 2) If is_specific is checked, hide non_detailed
        if (frm.doc.is_specific) {
          frm.set_df_property("non_detailed", "hidden", true);
        } else {
          frm.set_df_property("non_detailed", "hidden", false);
        }
    },
    non_detailed(frm) {
        // Re‑apply your hide/show logic whenever it changes
        frm.refresh();
    },
    
    is_specific(frm) {
        frm.refresh();
    },
    collection_received(frm) {
        const amt = frm.doc.collection_received;
        if (typeof amt === "number" && amt > 0) {
          // Use the built‑in money‑to‑words helper
          let words = frappe.utils.money_in_words(amt);
          
          // Ensure it ends with “Shillings ONLY”
          // (strip existing “only” if present, then append)
          words = words.replace(/\s*only\s*$/i, "").trim();
          words = words + " Shillings ONLY";
          
          frm.set_value("amount_in_words", words);
          frm.refresh_field("amount_in_words");
        }
    }
    
});
