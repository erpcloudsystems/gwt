from __future__ import unicode_literals
import frappe
from frappe import auth
import datetime
import json, ast


################ Quotation

@frappe.whitelist()
def quot_onload(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def quot_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_validate(doc, method=None):
    doc.total_fees = doc.transportation_fees + doc.lg_fees + doc.startup_fees + doc.extra_warranty_fees + doc.extra_fees
    for d in doc.items:
        d.valuation_rate = frappe.db.get_value('Bin', {'warehouse': d.warehouse, 'item_code': d.item_code},
                                               'valuation_rate')
        d.margin_type = None
        if doc.selling_price_list == "Victaulic Pricelist 2022" and doc.in_stock == 0:
            x = (d.price_list_rate - (d.supplier_discount * d.price_list_rate) / 100)
            d.supplier_discount_amount = x
            z = (x + (d.customs + d.s_c) * x / 100)
            d.cost_with_customs_and_s_c = z * d.qty
            d.estimated_cost = (z / (1 - (float(d.percentage) / 100))) * d.qty
            d.rate = d.estimated_cost / d.qty
            
        if doc.selling_price_list == "Grundfos Pricelist 2022":
            d.customs = 0
            d.s_c = 0
            d.supplier_discount = 0
            d.estimated_cost = float(d.price_list_rate) / (1 - (float(d.percentage) / 100))
            d.rate = float(d.price_list_rate) / (1 - (float(d.percentage) / 100))

        totals = 0
        total2 = 0
        total3 = 0
        total4 = float(0)
        total5 = 0
        total6 = 0
        for x in doc.items:
            total3 += float(x.qty) * float(x.supplier_discount_amount)
            doc.total_supplier_discount_amount = total3

            total4 += float(x.qty) * float(x.customs) * float(x.supplier_discount_amount) / 100
            doc.total_customs_amount = total4

            total5 += float(x.qty) * float(x.s_c) * float(x.supplier_discount_amount) / 100
            doc.total_s_c_amount = total5

            total6 += x.qty * x.price_list_rate
            doc.total_price_list_rate = total6

            total2 += x.cost_with_customs_and_s_c
            doc.total_cost_with_customs_and_s_c = total2

            totals += x.estimated_cost
            doc.total_estimated_selling_rate = totals

            doc.total_rate_margin_ = doc.total_estimated_selling_rate - doc.total_cost_with_customs_and_s_c
            doc.margin_average = ((doc.total_estimated_selling_rate - doc.total_cost_with_customs_and_s_c - doc.total_fees) / doc.total_estimated_selling_rate) * 100

        if doc.selling_price_list == "Grundfos Pricelist 2022" and doc.in_stock == 0:
            doc.total_cost_with_customs_and_s_c = doc.total_price_list_rate
            doc.total_estimated_selling_rate = doc.total
            doc.total_rate_margin_ = doc.total_estimated_selling_rate - doc.total_cost_with_customs_and_s_c
            doc.margin_average = ((doc.total_estimated_selling_rate - doc.total_cost_with_customs_and_s_c - doc.total_fees) / doc.total_estimated_selling_rate) * 100

        if doc.in_stock:
            d.estimated_cost = float(d.valuation_rate_stock) / (1 - (float(d.percentage) / 100))
            d.rate = d.estimated_cost

@frappe.whitelist()
def quot_validate(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_save(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_update(doc, method=None):
    pass


################ Sales Order


@frappe.whitelist()
def so_onload(doc, method=None):
    pass
@frappe.whitelist()
def so_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def so_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def so_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def so_validate(doc, method=None):
    pass
@frappe.whitelist()
def so_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def so_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def so_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def so_before_save(doc, method=None):
    pass
@frappe.whitelist()
def so_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def so_on_update(doc, method=None):
    pass


################ Delivery Note

@frappe.whitelist()
def dn_onload(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def dn_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_validate(doc, method=None):
    pass

@frappe.whitelist()
def dn_validate(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_submit(doc, method=None):
    new_doc = frappe.get_doc({
        "doctype": "Installation Note",
	"delivery_note": doc.name,
        "customer": doc.customer,
        "customer_group": doc.customer_group,
        "territory": doc.territory,
        "customer_address": doc.customer_address,
        "contact_person": doc.contact_person,
	"inst_date": doc.posting_date,
    })
    dn_items = frappe.db.sql(""" select a.name, a.idx, a.item_code, a.description, a.qty
                                   from `tabDelivery Note Item` a join `tabDelivery Note` b
                                   on a.parent = b.name
                                   where b.name = '{name}'
                               """.format(name=doc.name), as_dict=1)

    for c in dn_items:
        items = new_doc.append("items", {})
        items.idx = c.idx
        items.item_code = c.item_code
        items.description = c.description
        items.qty = c.qty
        items.prevdoc_detail_docname = c.name
        items.prevdoc_docname = doc.name
        items.prevdoc_doctype = "Delivery Note"


    new_doc.insert()
    frappe.msgprint(" Installation Note Record " + new_doc.name + " created ")

@frappe.whitelist()
def dn_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_save(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_update(doc, method=None):
    pass

################ Sales Invoice


@frappe.whitelist()
def siv_onload(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def siv_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def siv_validate(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_save(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_update(doc, method=None):
    pass


################ Payment Entry

@frappe.whitelist()
def pe_onload(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_insert(doc, method=None):
    pass
        
@frappe.whitelist()
def pe_after_insert(doc, method=None):
    pass
def pe_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def pe_validate(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_save(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_update(doc, method=None):
    pass

################ Material Request

@frappe.whitelist()
def mr_onload(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def mr_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def pe_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def mr_validate(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_save(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_update(doc, method=None):
    pass

################ Purchase Order

@frappe.whitelist()
def po_onload(doc, method=None):
    pass
@frappe.whitelist()
def po_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def po_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def po_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def po_validate(doc, method=None):
    pass
@frappe.whitelist()
def po_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def po_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def po_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def po_before_save(doc, method=None):
    pass
@frappe.whitelist()
def po_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def po_on_update(doc, method=None):
    pass

################ Purchase Receipt

@frappe.whitelist()
def pr_onload(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def pr_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def pr_validate(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_save(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_update(doc, method=None):
    pass


################ Purchase Invoice

@frappe.whitelist()
def piv_onload(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def piv_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def piv_validate(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_save(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_update(doc, method=None):
    pass

################ Employee Advance

@frappe.whitelist()
def emad_onload(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def emad_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def emad_validate(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_save(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_update(doc, method=None):
    pass

################ Expense Claim

@frappe.whitelist()
def excl_onload(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def excl_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def excl_validate(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_save(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_update(doc, method=None):
    pass

################ Stock Entry

@frappe.whitelist()
def ste_onload(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def ste_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def ste_validate(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_save(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_update(doc, method=None):
    pass

################ Blanket Order

@frappe.whitelist()
def blank_onload(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_insert(doc, method=None):
    pass
@frappe.whitelist()
def blank_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def blank_validate(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_save(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_update(doc, method=None):
    pass

