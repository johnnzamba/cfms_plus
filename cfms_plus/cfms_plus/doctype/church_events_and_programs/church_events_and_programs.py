# Copyright (c) 2025, John Kitheka and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ChurchEventsandPrograms(Document):
	pass
import frappe
from frappe.utils import formatdate
from frappe import _
from frappe.utils import formatdate, get_url

@frappe.whitelist()
def send_informative_notice_for(doc_name):
    """
    TEST helper: call this with a Church Events and Programs name
    to fire the 'awaiting review' email for that record.
    """
    # 1) fetch the document
    doc = frappe.get_doc("Church Events and Programs", doc_name)

    # 2) call your existing hook logic
    send_informative_notice(doc, None)

    return {"status": "queued", "name": doc_name}

def send_informative_notice(doc, method):
    """after_insert hook → queue review‑pending email to creator"""
    creator = doc.owner
    email = frappe.get_value("User", creator, "email")
    frappe.log_error(f"[send_informative_notice] owner={creator}, email={email}", "ChurchEvents")

    if not email:
        frappe.log_error(f"No email for {creator}", "ChurchEvents")
        return

    subject = _("✅ Your Event is Awaiting Review")
    body = f"""
        Hi {frappe.get_value('User', creator, 'full_name') or creator},<br><br>
        Your event <b>{doc.event_program_name}</b> is now pending review.<br>
        📅 {formatdate(doc.event_from)} – {formatdate(doc.end_date)}.<br><br>
        We’ll keep you posted on the next steps!<br><br>
        Cheers,<br>
        <i>Your Church Events Team</i>
    """

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=body,
        reference_doctype=doc.doctype,
        reference_name=doc.name
    )
    frappe.log_error(f"[send_informative_notice] queued to {email}", "ChurchEvents")

def handle_workflow_update(doc, method):
    """on_update → watch workflow_state and queue the right notices"""
    before = doc.get_doc_before_save()
    if not before or before.workflow_state == doc.workflow_state:
        return

    frappe.log_error(f"[handle_workflow_update] {before.workflow_state} → {doc.workflow_state}", "ChurchEvents")

    if doc.workflow_state == "Pending Finance":
        _notify_finance_managers(doc)

    elif doc.workflow_state == "Approved by Accounts":
        _notify_pastors(doc)

    # elif doc.workflow_state == "Approved by Senior Pastor":
    #     _notify_creator_approval(doc)
    #     _send_web_form(doc)

@frappe.whitelist()
def handle_final_approval(doc=None, method=None, doc_name=None):
    """
    on_submit hook (doc,status from hook), or test call via doc_name.
    """
    if doc_name:
        doc = frappe.get_doc("Church Events and Programs", doc_name)
    # if doc.docstatus != 1 or doc.workflow_state != "Approved by Senior Pastor":
    #     return {"status": "skipped"}
    _notify_creator_approval(doc)
    public_url = _create_event_web_form(doc)
    _dispatch_notice_of_event(doc, public_url)

    return {"status": "done", "url": public_url}

def _notify_finance_managers(doc):
    emails = [
        frappe.get_value("User", u.name, "email")
        for u in frappe.get_all("User",
                                filters={"church_branch": doc.church_branch},
                                fields=["name"])
        if "Accounts Manager" in frappe.get_roles(u.name)
           and frappe.get_value("User", u.name, "email")
    ]
    frappe.log_error(f"[_notify_finance_managers] to={emails}", "ChurchEvents")
    if not emails:
        return

    subject = _("💰 Budget Approval Needed")
    body = f"""
        Hello Finance,<br><br>
        <b>{doc.event_program_name}</b> (📅 {formatdate(doc.event_from)} – {formatdate(doc.end_date)})  
        in branch <b>{doc.church_branch}</b> is *Pending Finance*.<br><br>
        Proposed Budget: <b>Shs. {doc.event_budget:,.2f}</b>.<br><br>
        Please review and approve so we can proceed!<br><br>
        With Regards,<br>
        <i>AUTOGENERATED</i>
    """

    frappe.sendmail(
        recipients=emails,
        subject=subject,
        message=body,
        now=True,
        reference_doctype=doc.doctype,
        reference_name=doc.name
    )
    frappe.log_error("[_notify_finance_managers] queued", "ChurchEvents")


def _notify_pastors(doc):
    emails = [
        frappe.get_value("User", u.name, "email")
        for u in frappe.get_all("User",
                                filters={"church_branch": doc.church_branch},
                                fields=["name"])
        if "Pastor" in frappe.get_roles(u.name)
           and frappe.get_value("User", u.name, "email")
    ]
    frappe.log_error(f"[_notify_pastors] to={emails}", "ChurchEvents")
    if not emails:
        return

    subject = _("🙏 Event Ready for Final Approval")
    body = f"""
        Greetings Pastoral Team,<br><br>
        <b>{doc.event_program_name}</b> (📅 {formatdate(doc.event_from)} – {formatdate(doc.end_date)})  
        in branch <b>{doc.church_branch}</b> has been *Approved by Accounts*.<br><br>
        Proposed Budget: <b>Shs. {doc.event_budget:,.2f}</b>.<br><br>
        Please give your blessing so we can make it official!<br><br>
        With Regards,<br>
        <i>AUTOGENERATED</i>
    """

    frappe.sendmail(
        recipients=emails,
        subject=subject,
        message=body,
        now=True,
        reference_doctype=doc.doctype,
        reference_name=doc.name
    )
    frappe.log_error("[_notify_pastors] queued", "ChurchEvents")


def _notify_creator_approval(doc):
    creator   = doc.owner
    email     = frappe.get_value("User", creator, "email")
    full_name = frappe.get_value("User", creator, "full_name") or creator

    if not email:
        frappe.log_error(f"No email for creator {creator}", "ChurchEvents")
        return

    subject = _("🎉 Your Event is Fully Approved!")
    body = f"""
        Hey {full_name},<br><br>
        Fantastic news—your event <b>{doc.event_program_name}</b>  
        (📅 {formatdate(doc.event_from)} – {formatdate(doc.end_date)})  
        has been <b>approved by the Senior Pastor</b>. ✅<br><br>
        We’re all set—thank you! 🙌<br><br>
        Blessings,<br>
        <i>Your Church Events Team</i>
    """

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=body,
        now=True,
        reference_doctype=doc.doctype,
        reference_name=doc.name
    )


def _create_event_web_form(doc):
    """
    Create a Web Form for this event, save the URL back to doc.event_web_form,
    and return that URL.
    """
    wf = frappe.new_doc("Web Form")
    wf.title             = doc.event_program_name
    wf.doc_type          = "Questionnaire for Events and Programs"
    wf.module            = "Cfms Plus"
    wf.is_standard       = 1
    wf.introduction_text = doc.event_desc or ""
    wf.anonymous         = 1
    wf.allow_incomplete  = 1
    wf.button_label      = _("Confirm Attendance")
    wf.banner_image      = doc.get("event_poster") or doc.get("event_graphics") or ""
    wf.success_title     = _("Attendance Confirmed!")
    wf.success_message   = _("Thank you for confirming—looking forward to seeing you!")
    wf.published         = 1

    for field in [
        ("full_name","Data",_("What are your Full Names?"), 1, None),
        ("event_program","Link",_("Which event will you attend?"),1,"Church Events and Programs"),
        ("phone_number","Phone",_("What is your Phone Number?"),1,None),
        ("email_address","Data",_("Your Email Address"),0,None),
        ("gender","Select",_("What’s your Gender?"),1,"\nMale\nFemale\nOther"),
        ("additional_info","Small Text",_("Any other info?"),0,None),
        ("date","Date",_("Which date will you attend?"),0,None),
        ("attending","Check",_("I will be attending"),0,None),
    ]:
        wf.append("web_form_fields", dict(
            fieldname   = field[0],
            fieldtype   = field[1],
            label       = field[2],
            reqd        = field[3],
            options     = field[4]
        ))

    wf.insert(ignore_permissions=True)
    frappe.db.commit()

    url = f"{get_url().rstrip('/')}/{wf.route}"
    frappe.db.set_value(
        doc.doctype, doc.name,
        "event_web_form", url,
        update_modified=False
    )
    frappe.db.commit()

    return url

def _dispatch_notice_of_event(doc, webform_url):
    """
    Email every Church Member in the same branch, inviting them to register.
    """
    members = frappe.get_all(
        "Church Members",
        filters={"member_branch": doc.church_branch},
        fields=["member_email"]
    )
    emails = [m.member_email for m in members if m.member_email]
    if not emails:
        frappe.log_error(f"No Church Members in {doc.church_branch}", "ChurchEvents")
        return

    subject = _(f"🙌 Join us: {doc.event_program_name}")
    body = f"""
        Hello!<br><br>
        You’re invited to <b>{doc.event_program_name}</b>:  
        {formatdate(doc.event_from)} – {formatdate(doc.end_date)}.<br><br>
        {doc.event_desc or ""}<br><br>
        👉 Register here:<br>
        <a href="{webform_url}">{webform_url}</a><br><br>
        Regards,<br>
        <i>AUTOGENERATED</i>
    """

    attachments = []
    for img_field in ("event_poster","event_graphics","event_images"):
        img = doc.get(img_field)
        if img:
            attachments.append({"filename": img.split("/")[-1], "file_url": img})

    frappe.sendmail(
        recipients=emails,
        subject=subject,
        message=body,
        reference_doctype=doc.doctype,
        reference_name=doc.name
    )


# cmfs_plus
import json
import frappe
from frappe.desk.calendar import get_event_conditions

@frappe.whitelist()
def get_events(start, end, filters=None):
    """
    Called by the Calendar view to fetch events.
    Returns each event with exactly: id, title, start, end, color, allDay
    """
    filters = json.loads(filters or "{}")
    conditions = get_event_conditions("Church Events and Programs", filters)

    rows = frappe.db.sql(f"""
        SELECT
            name                  AS id,
            event_program_name    AS title,
            event_from            AS start,
            end_date              AS end,
            event_swatch          AS color,
			event_desc            AS description
        FROM `tabChurch Events and Programs`
        WHERE
            event_from <= %(end)s
            AND end_date   >= %(start)s
            {conditions}
    """, {"start": start, "end": end}, as_dict=True)

    # Mark them as all-day so FullCalendar won’t try to shift by your timezone
    for r in rows:
        r["allDay"] = True

    return rows

import frappe
from frappe.utils import nowdate, getdate
from urllib.parse import urlparse

def update_event_status():
    """Daily scheduler to update event_status and unpublish expired event webforms."""
    today = getdate(nowdate())
    events = frappe.get_all(
        "Church Events and Programs",
        fields=["name", "event_from", "end_date", "event_web_form"]
    )

    for ev in events:
        try:
            doc = frappe.get_doc("Church Events and Programs", ev.name)
            event_from = getdate(doc.event_from)
            end_date = getdate(doc.end_date)

            # 1) Determine new status
            if today < event_from:
                new_status = "Upcoming Event"
            elif event_from <= today <= end_date:
                new_status = "Live Event"
            else:
                new_status = "Event Expired"

            # 2) Update event_status if it changed
            if doc.event_status != new_status:
                doc.event_status = new_status
                doc.save(ignore_permissions=True)
                frappe.db.commit()

            # 3) If expired, unpublish its Web Form
            if new_status == "Event Expired" and doc.event_web_form:
                try:
                    # extract the route segment
                    parsed = urlparse(doc.event_web_form)
                    path = parsed.path.rstrip('/')
                    route = path.split('/')[-1]

                    if not route:
                        frappe.log_error(
                            f"No route segment in URL: {doc.event_web_form}",
                            "EventStatusCron"
                        )
                        continue

                    # find the Web Form by route
                    wf_list = frappe.get_all(
                        "Web Form",
                        filters={"route": route},
                        fields=["name", "published"]
                    )
                    if not wf_list:
                        frappe.log_error(
                            f"No Web Form for route '{route}'",
                            "EventStatusCron"
                        )
                        continue

                    wf_meta = wf_list[0]
                    if wf_meta.published:
                        wf = frappe.get_doc("Web Form", wf_meta.name)
                        wf.published = 0
                        wf.save(ignore_permissions=True)
                        frappe.db.commit()
                        frappe.log_error(
                            f"Unpublished Web Form '{wf.name}' for event '{doc.name}'",
                            "EventStatusCron"
                        )

                except Exception as wf_exc:
                    frappe.log_error(
                        f"Error unpublishing Web Form for '{doc.name}': {wf_exc}",
                        "EventStatusCron"
                    )

        except Exception as e:
            frappe.log_error(
                f"Error processing event '{ev.name}': {e}",
                "EventStatusCron"
            )


def update_event_status(doc=None, method=None):
    """
    Called via after_insert hook.
    Updates status of ALL Church Events and Programs based on today's date.
    """
    today = getdate(nowdate())
    events = frappe.get_all("Church Events and Programs", fields=["name", "event_from", "end_date"])

    for ev in events:
        event_doc = frappe.get_doc("Church Events and Programs", ev.name)
        event_from = getdate(event_doc.event_from)
        end_date = getdate(event_doc.end_date)

        if today < event_from:
            event_doc.event_status = "Upcoming Event"
        elif event_from <= today <= end_date:
            event_doc.event_status = "Live Event"
        elif today > end_date:
            event_doc.event_status = "Event Expired"
        else:
            continue

        event_doc.save(ignore_permissions=True)

    frappe.db.commit()