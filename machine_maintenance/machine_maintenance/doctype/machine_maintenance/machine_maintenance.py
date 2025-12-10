import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, flt
from erpnext.accounts.utils import get_company_default
from erpnext.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account


class MachineMaintenance(Document):

    # --------------------------------------
    # VALIDATIONS
    # --------------------------------------
    def validate(self):
        self.validate_dates()
        self.calculate_total_cost()
        self.validate_technician_on_submit()
        self.set_overdue_if_needed()

    def validate_dates(self):
        if self.maintenance_date and self.completion_date:
            if getdate(self.completion_date) < getdate(self.maintenance_date):
                frappe.throw("Completion Date cannot be earlier than Maintenance Date.")

    def validate_technician_on_submit(self):
        # Only check when document is being submitted (docstatus = 1)
        if self.docstatus == 1 and not self.technician:
            frappe.throw("Technician must be assigned before submitting the record.")

    # --------------------------------------
    # COST CALCULATION (SERVER-SIDE)
    # --------------------------------------
    def calculate_total_cost(self):
        total = 0
        for row in self.parts_used or []:
            row.amount = flt(row.quantity) * flt(row.rate)
            total += row.amount
        self.cost = total

    # --------------------------------------
    # AUTO OVERDUE LOGIC
    # --------------------------------------
    def set_overdue_if_needed(self):
        if self.maintenance_date and self.status != "Completed":
            if getdate(self.maintenance_date) < getdate(nowdate()):
                self.status = "Overdue"

    # --------------------------------------
    # ON SUBMIT → CREATE JOURNAL ENTRY
    # --------------------------------------
    def on_submit(self):
        if self.cost <= 0:
            frappe.throw("Cost must be greater than zero before submitting.")

        self.create_journal_entry()

    def create_journal_entry(self):
        """Creates a Journal Entry on submission"""

        company = frappe.db.get_single_value("Global Defaults", "default_company")
        if not company:
            frappe.throw("Please set a Default Company in Global Defaults.")

        # Expense account (set in company defaults)
        expense_account = (
            get_company_default(company, "default_expense_account")
            or get_company_default(company, "expenses_included_in_valuation")
        )

        if not expense_account:
            frappe.throw("Please set a Maintenance Expense Account in Company Defaults.")

        # Get Default Cash/Bank Account
        bank_cash = get_default_bank_cash_account(company)
        if not bank_cash or not bank_cash.get("account"):
            frappe.throw("Please set a Default Cash or Bank Account for the company.")

        credit_account = bank_cash.get("account")
        amount = flt(self.cost)

        # Create Journal Entry
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = company
        je.posting_date = self.maintenance_date or nowdate()
        je.user_remark = f"Maintenance cost entry for {self.machine_name}"

        # Debit Maintenance Expense
        je.append("accounts", {
            "account": expense_account,
            "debit_in_account_currency": amount,
            "debit": amount,
            "reference_type": self.doctype,
            "reference_name": self.name,
        })

        # Credit Cash/Bank
        je.append("accounts", {
            "account": credit_account,
            "credit_in_account_currency": amount,
            "credit": amount,
            "reference_type": self.doctype,
            "reference_name": self.name,
        })

        je.flags.ignore_permissions = True
        je.insert()
        je.submit()

        frappe.msgprint(f"Journal Entry <b>{je.name}</b> created for maintenance cost.")
