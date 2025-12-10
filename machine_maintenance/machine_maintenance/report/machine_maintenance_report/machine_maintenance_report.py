import frappe

def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    # Row formatting based on Status
    for row in data:
        status = row.get("status")
        if status == "Overdue":
            row["indicator_color"] = "red"
        elif status == "Scheduled":
            row["indicator_color"] = "yellow"
        elif status == "Completed":
            row["indicator_color"] = "green"

    return columns, data


def get_columns():
    return [
        {"label": "Machine", "fieldname": "machine_name", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Maintenance Date", "fieldname": "maintenance_date", "fieldtype": "Date", "width": 120},
        {"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Status", "fieldname": "status", "width": 120},
        {"label": "Total Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    consolidated = filters.get("consolidated")

    conditions = "1=1"
    values = {}

    if filters.get("machine"):
        conditions += " AND machine_name = %(machine)s"
        values["machine"] = filters["machine"]

    if filters.get("technician"):
        conditions += " AND technician = %(technician)s"
        values["technician"] = filters["technician"]

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND maintenance_date BETWEEN %(from)s AND %(to)s"
        values["from"] = filters["from_date"]
        values["to"] = filters["to_date"]

    # Consolidated View → Group by Machine
    if consolidated:
        return frappe.db.sql(f"""
            SELECT 
                machine_name,
                SUM(cost) AS cost,
                NULL AS maintenance_date,
                NULL AS technician,
                'Consolidated' AS status
            FROM `tabMachine Maintenance`
            WHERE docstatus < 2 AND {conditions}
            GROUP BY machine_name
        """, values, as_dict=True)

    # Normal View → Detailed rows
    return frappe.db.sql(f"""
        SELECT 
            machine_name,
            maintenance_date,
            technician,
            status,
            cost
        FROM `tabMachine Maintenance`
        WHERE docstatus < 2 AND {conditions}
        ORDER BY maintenance_date DESC
    """, values, as_dict=True)
