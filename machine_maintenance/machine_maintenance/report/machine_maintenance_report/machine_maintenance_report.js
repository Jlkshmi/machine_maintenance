frappe.query_reports["Machine Maintenance Report"] = {
    filters: [
        {
            fieldname: "machine",
            label: "Machine",
            fieldtype: "Link",
            options: "Item"
        },
        {
            fieldname: "technician",
            label: "Technician",
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end()
        },
        {
            fieldname: "consolidated",
            label: "Consolidated",
            fieldtype: "Check",
            default: 0
        }
    ]
};
