import frappe



def get_columns(consolidated=False):
    if consolidated:
        return [
            {"label": "Machine", "fieldname": "machine", "fieldtype": "Link", "options": "Item", "width": 200},
            {"label": "Total Maintenance Cost", "fieldname": "total_cost", "fieldtype": "Currency", "width": 180}
        ]
    else:
        return [
            {"label": "Machine", "fieldname": "machine", "fieldtype": "Link", "options": "Item", "width": 180},
            {"label": "Maintenance Date", "fieldname": "maintenance_date", "fieldtype": "Date", "width": 120},
            {"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "Employee", "width": 150},
            {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
            {"label": "Total Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 120}
        ]

def execute(filters=None):
    filters = filters or {}
    consolidated = filters.get("consolidated")

    columns = get_columns(consolidated)
    data = get_data(filters, consolidated)

    return columns, data


def get_conditions(filters):
    conditions = []
    values = {}

    if filters.get("machine"):
        conditions.append("machine_name = %(machine)s")
        values["machine"] = filters["machine"]

    if filters.get("technician"):
        conditions.append("technician = %(technician)s")
        values["technician"] = filters["technician"]

    if filters.get("from_date"):
        conditions.append("maintenance_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("maintenance_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    return " AND ".join(conditions), values


def get_non_consolidated_data(filters):
    conditions, values = get_conditions(filters)

    query = f"""
        SELECT
            machine_name AS machine,
            maintenance_date,
            technician,
            status,
            cost
        FROM `tabMachine Maintenance`
        WHERE docstatus < 2
        {f"AND {conditions}" if conditions else ""}
        ORDER BY maintenance_date DESC
    """

    data = frappe.db.sql(query, values, as_dict=True)

    # Row coloring based on status
    for row in data:
        if row.status == "Overdue":
            row["__style"] = "background-color: #ffe6e6"
        elif row.status == "Scheduled":
            row["__style"] = "background-color: #fff7cc"
        elif row.status == "Completed":
            row["__style"] = "background-color: #e6ffed"

    return data

def get_consolidated_data(filters):
    conditions, values = get_conditions(filters)

    query = f"""
        SELECT
            machine_name AS machine,
            SUM(cost) AS total_cost
        FROM `tabMachine Maintenance`
        WHERE docstatus < 2
        {f"AND {conditions}" if conditions else ""}
        GROUP BY machine_name
        ORDER BY machine_name
    """

    return frappe.db.sql(query, values, as_dict=True)

def get_data(filters, consolidated):
    if consolidated:
        return get_consolidated_data(filters)
    else:
        return get_non_consolidated_data(filters)
