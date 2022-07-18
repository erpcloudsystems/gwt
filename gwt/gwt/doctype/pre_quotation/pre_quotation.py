
import frappe
from frappe.model.document import Document

class PreQuotation(Document):
    @frappe.whitelist()
    def before_validate(self):
        for x in self.items:
            bundle_items = frappe.db.sql(""" select a.parent_item, a.idx, a.item_code,a.rate,a.amount,a.description,a.qty
                                                       from `tabNew Product Bundle Item` a join `tabNew Product Bundle` b
                                                       on a.parent = b.name
                                                       where b.new_item_code = '{name}'
                                                   """.format(name=x.item_code), as_dict=1)

            for y in bundle_items:
                items = self.append("packed_items", {})
                items.idx = y.idx
                items.item_code = y.item_code
                items.parent_item = y.parent_item
                items.description = y.description
                items.qty = y.qty
                items.rate = y.rate
                items.amount = y.amount

            for z in self.packed_items:
                if z.rate == 0:
                    frappe.throw("Row #" + str(z.idx) + ": Rate Cannot Be Zero In The Bundle Items Table ")

    @frappe.whitelist()
    def validate(self):
        self.total_fees = self.transportation_fees + self.lg_fees + self.startup_fees + self.extra_warranty_fees + self.extra_fees
        totals = 0
        total2 = 0
        total3 = 0
        total4 = float(0)
        total5 = 0
        total6 = 0

        for d in self.items:
            if d.bundle_item and not d.price_list_rate:
                frappe.throw("Row #" + str(d.idx) + ": Price List Rate Cannot Be Zero, Put Any Value And It Will Be Calculated Automatically From The Packed Items Table ")

            if d.bundle_item == 1:
                d.price_list_rate = 0

            for x in self.packed_items:
                if d.item_code == x.parent_item:
                    x.amount = x.rate * x.qty
                    d.price_list_rate += (x.amount / d.qty) / self.conversion_rate

            d.valuation_rate = frappe.db.get_value('Bin', {'warehouse': d.warehouse, 'item_code': d.item_code},
                                                   'valuation_rate')
            d.margin_type = None

            if d.in_stock:
                d.estimated_cost = float(d.valuation_rate_stock) / (1 - (float(d.percentage) / 100))
                d.rate = d.estimated_cost
            if self.manual_price == 0:
                if self.selling_price_list == "Victaulic Pricelist 2022" and d.in_stock == 0:
                    x = (float(d.price_list_rate) - (float(d.supplier_discount) * float(d.price_list_rate)) / 100)
                    d.supplier_discount_amount = x
                    z = (x + (float(d.customs) + float(d.s_c)) * x / 100)
                    d.cost_with_customs_and_s_c = z * d.qty
                    d.estimated_cost = (z / (1 - (float(d.percentage) / 100))) * d.qty
                    d.rate = d.estimated_cost / d.qty

                    total3 += float(d.qty) * float(d.supplier_discount_amount)
                    self.total_supplier_discount_amount = total3

                    total4 += float(d.qty) * float(d.customs) * float(d.supplier_discount_amount) / 100
                    self.total_customs_amount = total4

                    total5 += float(d.qty) * float(d.s_c) * float(d.supplier_discount_amount) / 100
                    self.total_s_c_amount = total5

                    total6 += d.qty * d.price_list_rate
                    self.total_price_list_rate = total6

                    total2 += d.cost_with_customs_and_s_c
                    self.total_cost_with_customs_and_s_c = total2

                    totals += d.estimated_cost
                    self.total_estimated_selling_rate = totals

                    self.total_rate_margin_ = float(self.total_estimated_selling_rate) - float(
                        self.total_cost_with_customs_and_s_c) - float(self.total_fees) - float(self.discount_amount)
                    self.margin_average = (( self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees - self.discount_amount) / self.total_estimated_selling_rate) * 100

                if self.selling_price_list == "Watts Pricelist 2022 Stock" and d.in_stock == 0:
                    x = (float(d.price_list_rate) - (float(d.supplier_discount) * float(d.price_list_rate)) / 100)
                    d.supplier_discount_amount = x
                    z = (x + (float(d.customs) + float(d.s_c)) * x / 100)
                    d.cost_with_customs_and_s_c = z * d.qty
                    d.estimated_cost = (z / (1 - (float(d.percentage) / 100))) * d.qty
                    d.rate = d.estimated_cost / d.qty

                    total3 += float(d.qty) * float(d.supplier_discount_amount)
                    self.total_supplier_discount_amount = total3

                    total4 += float(d.qty) * float(d.customs) * float(d.supplier_discount_amount) / 100
                    self.total_customs_amount = total4

                    total5 += float(d.qty) * float(d.s_c) * float(d.supplier_discount_amount) / 100
                    self.total_s_c_amount = total5

                    total6 += d.qty * d.price_list_rate
                    self.total_price_list_rate = total6

                    total2 += d.cost_with_customs_and_s_c
                    self.total_cost_with_customs_and_s_c = total2

                    totals += d.estimated_cost
                    self.total_estimated_selling_rate = totals

                    self.total_rate_margin_ = float(self.total_estimated_selling_rate) - float(
                        self.total_cost_with_customs_and_s_c) - float(self.total_fees) - float(self.discount_amount)
                    self.margin_average = (( self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees - self.discount_amount) / self.total_estimated_selling_rate) * 100

                if self.selling_price_list == "Grundfos Pricelist 2022" and d.in_stock == 0:
                    d.customs = 0
                    d.s_c = 0
                    d.supplier_discount = 0
                    d.estimated_cost = float(d.price_list_rate) / (1 - (float(d.percentage) / 100))
                    d.rate = float(d.price_list_rate) / (1 - (float(d.percentage) / 100))
                    d.amount = d.rate * d.qty
                    total6 += d.qty * d.price_list_rate
                    self.total_price_list_rate = total6
                    self.total_cost_with_customs_and_s_c = total6
                    self.total_estimated_selling_rate = self.total
                    self.total_rate_margin_ = float(self.total_estimated_selling_rate) - float(self.total_cost_with_customs_and_s_c) - float(self.total_fees) - float(self.discount_amount)
                    self.margin_average = ((self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees - self.discount_amount) / self.total_estimated_selling_rate) * 100

            if self.manual_price == 1:
                if self.selling_price_list == "Victaulic Pricelist 2022" and d.in_stock == 0:
                    d.margin = 0
                    x = (float(d.price_list_rate) - (float(d.supplier_discount) * float(d.price_list_rate)) / 100)
                    d.supplier_discount_amount = x
                    z = (x + (float(d.customs) + float(d.s_c)) * x / 100)
                    d.cost_with_customs_and_s_c = z * d.qty
                    d.estimated_cost = d.rate * d.qty
                    d.percentage = ((d.estimated_cost - d.cost_with_customs_and_s_c) / d.estimated_cost) * 100

                    total3 += float(d.qty) * float(d.supplier_discount_amount)
                    self.total_supplier_discount_amount = total3

                    total4 += float(d.qty) * float(d.customs) * float(d.supplier_discount_amount) / 100
                    self.total_customs_amount = total4

                    total5 += float(d.qty) * float(d.s_c) * float(d.supplier_discount_amount) / 100
                    self.total_s_c_amount = total5

                    total6 += d.qty * d.price_list_rate
                    self.total_price_list_rate = total6

                    total2 += d.cost_with_customs_and_s_c
                    self.total_cost_with_customs_and_s_c = total2

                    totals += d.estimated_cost
                    self.total_estimated_selling_rate = totals

                    self.total_rate_margin_ = self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees - self.discount_amount
                    self.margin_average = ((self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees - self.discount_amount) / self.total_estimated_selling_rate) * 100

                if self.selling_price_list == "Watts Pricelist 2022 Stock" and d.in_stock == 0:
                    d.margin = 0
                    x = (float(d.price_list_rate) - (float(d.supplier_discount) * float(d.price_list_rate)) / 100)
                    d.supplier_discount_amount = x
                    z = (x + (float(d.customs) + float(d.s_c)) * x / 100)
                    d.cost_with_customs_and_s_c = z * d.qty
                    d.estimated_cost = d.rate * d.qty
                    d.percentage = ((d.estimated_cost - d.cost_with_customs_and_s_c) / d.estimated_cost) * 100

                    total3 += float(d.qty) * float(d.supplier_discount_amount)
                    self.total_supplier_discount_amount = total3

                    total4 += float(d.qty) * float(d.customs) * float(d.supplier_discount_amount) / 100
                    self.total_customs_amount = total4

                    total5 += float(d.qty) * float(d.s_c) * float(d.supplier_discount_amount) / 100
                    self.total_s_c_amount = total5

                    total6 += d.qty * d.price_list_rate
                    self.total_price_list_rate = total6

                    total2 += d.cost_with_customs_and_s_c
                    self.total_cost_with_customs_and_s_c = total2

                    totals += d.estimated_cost
                    self.total_estimated_selling_rate = totals

                    self.total_rate_margin_ = self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees - self.discount_amount
                    self.margin_average = ((self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees - self.discount_amount) / self.total_estimated_selling_rate) * 100

                if self.selling_price_list == "Grundfos Pricelist 2022" and d.in_stock == 0:
                    d.percentage = 0
                    d.customs = 0
                    d.s_c = 0
                    d.supplier_discount = 0
                    d.estimated_cost = d.rate * d.qty
                    d.cost_with_customs_and_s_c = d.price_list_rate * d.qty
                    d.percentage = ((d.estimated_cost - d.cost_with_customs_and_s_c) / d.estimated_cost) * 100
                    d.amount = d.rate * d.qty
                    total6 += d.qty * d.price_list_rate
                    self.total_price_list_rate = total6
                    self.total_cost_with_customs_and_s_c = total6
                    self.total_estimated_selling_rate = self.net_total
                    self.total_rate_margin_ = self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees
                    self.margin_average = ((self.total_estimated_selling_rate - self.total_cost_with_customs_and_s_c - self.total_fees) / self.total_estimated_selling_rate) * 100


    def on_submit(self, method=None):
        new_doc = frappe.get_doc({
            "doctype": "Quotation",
            "transaction_date": self.transaction_date,
            "pre_quotation": self.name,
            "quotation_to": "Customer",
            "party_name": self.party_name,
            "project": self.project,
            "currency": self.currency,
            "conversion_rate": self.conversion_rate,
            "price_list_currency": self.price_list_currency,
            "plc_conversion_rate": self.plc_conversion_rate,
            "selling_price_list": self.selling_price_list,

        })
        pre_items = frappe.db.sql(""" select a.name, a.idx, a.item_code,a.rate,a.amount,a.description,a.qty,a.price_list_rate,a.base_price_list_rate
                                           from `tabPre Quotation Item` a join `tabPre Quotation` b
                                           on a.parent = b.name
                                           where b.name = '{name}'
                                       """.format(name=self.name), as_dict=1)

        for c in pre_items:
            items = new_doc.append("items", {})
            items.idx = c.idx
            items.item_code = c.item_code
            items.item_name = c.item_name
            items.description = c.description
            items.price_list_rate = c.price_list_rate
            items.base_price_list_rate = c.base_price_list_rate
            items.qty = c.qty
            items.rate = c.rate
            items.amount = c.amount


        new_doc.insert()
        frappe.msgprint(" New Quotation" + new_doc.name + " created ")