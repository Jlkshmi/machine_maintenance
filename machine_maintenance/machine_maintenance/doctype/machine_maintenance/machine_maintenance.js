frappe.ui.form.on('Machine Maintenance', {
    onload(frm) {
        if (frm.is_new() && !frm.doc.maintenance_date) {
            frm.set_value('maintenance_date', frappe.datetime.get_today());
        }
    },

    refresh(frm) {
        frm.toggle_display('notes', frm.doc.status !== 'Scheduled');

        if (frm.doc.docstatus === 0 && frm.doc.status !== 'Completed') {
            frm.add_custom_button(__('Mark Completed'), () => {
                frm.set_value('status', 'Completed');
                frm.set_value('completion_date', frappe.datetime.get_today());
                frm.save();
            });
        }
    },

    status(frm) {
        frm.toggle_display('notes', frm.doc.status !== 'Scheduled');
    },

    maintenance_date(frm) {
        let today = frappe.datetime.get_today();
        if (frm.doc.maintenance_date < today && frm.doc.status !== "Completed") {
            frm.set_value("status", "Overdue");
        }
    }
});

frappe.ui.form.on('Parts Used', {
    quantity(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    rate(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    parts_used_remove(frm) {
        compute_total_cost(frm);
    }
});

function calculate_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    row.amount = (row.quantity || 0) * (row.rate || 0);
    frm.refresh_field("parts_used");
    compute_total_cost(frm);
}

function compute_total_cost(frm) {
    let total = 0;
    (frm.doc.parts_used || []).forEach(row => {
        total += row.amount || 0;
    });

    frm.set_value("cost", total);
    frm.refresh_field("cost");
}
