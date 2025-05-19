app_name = "cfms_plus"
app_title = "Cfms Plus"
app_publisher = "John Kitheka"
app_description = "An ENhanced Church Finance and ERP System"
app_email = "nzambakitheka@gmail.com"
app_license = "mit"

# Apps
# ------------------
# Hook on document methods and events

doc_events = {
	"Church Branch": {
		"after_insert": "cfms_plus.cfms_plus.doctype.church_branch.church_branch.create_coa",
	},
    "Church Members": {
		"after_insert": "cfms_plus.cfms_plus.doctype.church_members.church_members.generate_member_id",
	},
    "Church Events and Programs": {
        "after_insert": [
            "cfms_plus.cfms_plus.doctype.church_events_and_programs.church_events_and_programs.send_informative_notice",
            "cfms_plus.cfms_plus.doctype.church_events_and_programs.church_events_and_programs.update_event_status"
    ],
        "on_update":    "cfms_plus.cfms_plus.doctype.church_events_and_programs.church_events_and_programs.handle_workflow_update",
        "on_submit": "cfms_plus.cfms_plus.doctype.church_events_and_programs.church_events_and_programs.handle_final_approval"
    },
    "Questionnaire for Events and Programs": {
		"after_insert": "cfms_plus.cfms_plus.doctype.questionnaire_for_events_and_programs.questionnaire_for_events_and_programs.save_attendance",
	},
    "Church Services Attendance": {
		"on_submit": "cfms_plus.cfms_plus.doctype.church_services_attendance.church_services_attendance.update_member_attendance",
	},
    "Church Collections": {
        "after_insert": "cfms_plus.cfms_plus.doctype.church_collections.church_collections.update_member",
        "on_submit": "cfms_plus.cfms_plus.doctype.church_collections.church_collections.create_journal_entry"
    }
    # "Event or Program Attendance TOOL": {
	# 	"after_insert": "cfms_plus.cfms_plus.doctype.event_or_program_attendance_tool.event_or_program_attendance_tool.mark_event_attendance",
	# }
}

scheduler_events = {
    "daily": [
        "cfms_plus.cfms_plus.doctype.church_events_and_programs.church_events_and_programs.update_event_status"
    ]
}
# required_apps = []

fixtures = [
    {
        "doctype": "DocType",
        "filters": [
            [
                "name", "in", [
                    "User"
                ]
            ]
        ]
    },
    {
        "doctype": "Email Template",
        "filters": [["name", "in", ["Church Members Giving Acknowledgement"]]]
    },
    {
        "doctype": "Client Script",
        "filters": [["name", "in", ["Register Member to Group/Ministry", "Register in Group/Ministry Doc", "Events/Programs Calendar"]]]
    },
    {
        "doctype": "Workflow",
        "filters": [["name", "in", ["Event/Program Workflow"]]]
    },
    {
        "doctype": "Workflow State"
    },
    {
        "doctype": "Workflow Action Master"
    },
    {
        "doctype": "Workspace",
        "filters": [["name", "in", ["CFMS +"]]]
    },
    {
        "doctype": "Role",
        "filters": [["name", "in", ["Pastor"]]]
    }
]
# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "cfms_plus",
# 		"logo": "/assets/cfms_plus/logo.png",
# 		"title": "Cfms Plus",
# 		"route": "/cfms_plus",
# 		"has_permission": "cfms_plus.api.permission.has_app_permission"
# 	}
# ]

calendar_js = {
    "Church Events and Programs": "public/js/church_events_and_programs.js"
}

# register the calendar class
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cfms_plus/css/cfms_plus.css"
# app_include_js = "/assets/cfms_plus/js/cfms_plus.js"

# include js, css files in header of web template
# web_include_css = "/assets/cfms_plus/css/cfms_plus.css"
# web_include_js = "/assets/cfms_plus/js/cfms_plus.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cfms_plus/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "cfms_plus/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "cfms_plus.utils.jinja_methods",
# 	"filters": "cfms_plus.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "cfms_plus.install.before_install"
# after_install = "cfms_plus.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "cfms_plus.uninstall.before_uninstall"
# after_uninstall = "cfms_plus.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "cfms_plus.utils.before_app_install"
# after_app_install = "cfms_plus.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "cfms_plus.utils.before_app_uninstall"
# after_app_uninstall = "cfms_plus.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cfms_plus.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"cfms_plus.tasks.all"
# 	],
# 	"daily": [
# 		"cfms_plus.tasks.daily"
# 	],
# 	"hourly": [
# 		"cfms_plus.tasks.hourly"
# 	],
# 	"weekly": [
# 		"cfms_plus.tasks.weekly"
# 	],
# 	"monthly": [
# 		"cfms_plus.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "cfms_plus.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cfms_plus.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cfms_plus.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["cfms_plus.utils.before_request"]
# after_request = ["cfms_plus.utils.after_request"]

# Job Events
# ----------
# before_job = ["cfms_plus.utils.before_job"]
# after_job = ["cfms_plus.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"cfms_plus.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

