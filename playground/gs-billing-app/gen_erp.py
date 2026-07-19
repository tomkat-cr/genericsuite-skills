import os
import json

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "config_dbdef")
frontend_dir = os.path.join(base_dir, "frontend")
backend_dir = os.path.join(base_dir, "backend")

os.makedirs(frontend_dir, exist_ok=True)
os.makedirs(backend_dir, exist_ok=True)


def generate_entity(
    name, title, component, url, table_name, fields,
    type="master", parentUrl=None, childComponents=None,
    backend_extras=None
):
    # frontend
    frontend = {
        "baseUrl": url,
        "title": title,
        "name": title[:-1] if title.endswith('s') else title,
        "component": component,
        "dbApiUrl": url,
    }

    if type == "child_listing":
        frontend["type"] = "child_listing"
        frontend["subType"] = "table"
        frontend["parentUrl"] = parentUrl
        frontend["endpointKeyNames"] = [
            {"parameterName": f"{parentUrl}_id", "parentElementName": "id"}]
    else:
        if childComponents:
            frontend["childComponents"] = childComponents

    frontend_fields = [
        {"name": "id", "required": True, "label": "ID",
            "type": "_id", "readonly": True, "hidden": True},
        {"name": "user_id", "required": True, "label": "User ID",
            "type": "text", "readonly": True, "hidden": True}
    ]
    frontend_fields.extend(fields)
    frontend_fields.extend([
        {
            "name": "creation_date",
            "required": True,
            "label": "Created",
            "type": "datetime-local",
            "readonly": True,
            "hidden": False,
            "default_value": "current_timestamp",
            "listing": True
        },
        {
            "name": "update_date",
            "required": True,
            "label": "Last update",
            "type": "datetime-local",
            "readonly": True,
            "hidden": False,
            "default_value": "current_timestamp",
            "listing": False}
    ])
    frontend["fieldElements"] = frontend_fields

    with open(os.path.join(frontend_dir, f"{name}.json"), "w") as f:
        json.dump(frontend, f, indent=4)

    # backend
    backend = {"table_name": table_name}
    if backend_extras:
        backend.update(backend_extras)

    with open(os.path.join(backend_dir, f"{name}.json"), "w") as f:
        json.dump(backend, f, indent=4)


entities = [
    # Accounting
    {
        "name": "accounts",
        "title": "Accounts",
        "component": "Accounts",
        "url": "accounts",
        "table_name": "accounts",
        "fields": [
            {"name": "code", "required": True, "label": "Account Code",
                "type": "text", "listing": True},
            {"name": "name", "required": True, "label": "Account Name",
                "type": "text", "listing": True},
            {"name": "type", "required": True, "label": "Type",
             "type": "select", "select_elements": [
                 "Asset", "Liability", "Equity", "Revenue", "Expense"],
             "listing": True}
        ]
    },
    {
        "name": "journal_entries",
        "title": "Journal Entries",
        "component": "JournalEntries",
        "url": "journal_entries",
        "table_name": "journal_entries",
        "childComponents": ["JournalLines"],
        "fields": [
            {"name": "date", "required": True, "label": "Date",
                "type": "date", "listing": True},
            {"name": "description", "required": True,
                "label": "Description", "type": "text",
                "listing": True},
            {"name": "status", "required": True, "label": "Status",
             "type": "select",
             "select_elements": ["Draft", "Posted"],
             "listing": True}
        ]
    },
    {
        "name": "journal_lines",
        "title": "Journal Lines",
        "component": "JournalLines",
        "url": "journal_lines",
        "table_name": "journal_lines",
        "type": "child_listing", "parentUrl": "journal_entries",
        "fields": [
            {"name": "account_id", "required": True, "label": "Account",
                "type": "select_table", "listing": True},
            {"name": "debit", "required": False, "label": "Debit",
                "type": "number", "listing": True},
            {"name": "credit", "required": False, "label": "Credit",
                "type": "number", "listing": True}
        ]
    },

    # Sales
    {
        "name": "customers", "title": "Customers", "component": "Customers",
        "url": "customers", "table_name": "customers",
        "fields": [
            {"name": "name", "required": True, "label": "Company Name",
                "type": "text", "listing": True},
            {"name": "email", "required": False, "label": "Email",
                "type": "email", "listing": True},
            {"name": "phone", "required": False,
                "label": "Phone", "type": "text", "listing": True}
        ]
    },
    {
        "name": "invoices", "title": "Invoices", "component": "Invoices",
        "url": "invoices", "table_name": "invoices",
        "childComponents": ["InvoiceLines"],
        "fields": [
            {"name": "customer_id", "required": True, "label": "Customer",
                "type": "select_table", "listing": True},
            {"name": "invoice_date", "required": True,
                "label": "Date", "type": "date", "listing": True},
            {"name": "total", "required": True, "label": "Total Amount",
                "type": "number", "listing": True}
        ]
    },
    {
        "name": "invoice_lines", "title": "Invoice Lines",
        "component": "InvoiceLines", "url": "invoice_lines",
        "table_name": "invoice_lines",
        "type": "child_listing", "parentUrl": "invoices",
        "fields": [
            {"name": "description", "required": True,
                "label": "Item Description", "type": "text", "listing": True},
            {"name": "quantity", "required": True, "label": "Qty",
                "type": "number", "listing": True},
            {"name": "price", "required": True, "label": "Unit Price",
                "type": "number", "listing": True}
        ]
    },

    # Purchasing
    {
        "name": "vendors", "title": "Vendors", "component": "Vendors",
        "url": "vendors", "table_name": "vendors",
        "fields": [
            {"name": "name", "required": True, "label": "Vendor Name",
                "type": "text", "listing": True},
            {"name": "email", "required": False, "label": "Email",
                "type": "email", "listing": True},
            {"name": "contact_person", "required": False,
                "label": "Contact", "type": "text", "listing": True}
        ]
    },
    {
        "name": "purchase_orders", "title": "Purchase Orders",
        "component": "PurchaseOrders", "url": "purchase_orders",
        "table_name": "purchase_orders",
        "childComponents": ["PoLines"],
        "fields": [
            {"name": "vendor_id", "required": True, "label": "Vendor",
                "type": "select_table", "listing": True},
            {"name": "order_date", "required": True,
                "label": "Date", "type": "date", "listing": True},
            {"name": "total", "required": True, "label": "Total Amount",
                "type": "number", "listing": True}
        ]
    },
    {
        "name": "po_lines", "title": "PO Lines", "component": "PoLines",
        "url": "po_lines", "table_name": "po_lines",
        "type": "child_listing", "parentUrl": "purchase_orders",
        "fields": [
            {"name": "item", "required": True, "label": "Item",
                "type": "text", "listing": True},
            {"name": "quantity", "required": True, "label": "Qty",
                "type": "number", "listing": True},
            {"name": "price", "required": True, "label": "Price",
                "type": "number", "listing": True}
        ]
    },

    # Banking
    {
        "name": "bank_accounts", "title": "Bank Accounts",
        "component": "BankAccounts", "url": "bank_accounts",
        "table_name": "bank_accounts",
        "childComponents": ["BankTransactions"],
        "fields": [
            {"name": "bank_name", "required": True,
                "label": "Bank Name", "type": "text", "listing": True},
            {"name": "account_number", "required": True,
                "label": "Account Number", "type": "text", "listing": True},
            {"name": "currency", "required": True,
                "label": "Currency", "type": "text", "listing": True}
        ]
    },
    {
        "name": "bank_transactions", "title": "Bank Transactions",
        "component": "BankTransactions", "url": "bank_transactions",
        "table_name": "bank_transactions",
        "type": "child_listing", "parentUrl": "bank_accounts",
        "fields": [
            {"name": "transaction_date", "required": True,
                "label": "Date", "type": "date", "listing": True},
            {"name": "description", "required": True,
                "label": "Description", "type": "text", "listing": True},
            {"name": "amount", "required": True, "label": "Amount",
                "type": "number", "listing": True},
            {"name": "type", "required": True, "label": "Type",
             "type": "select",
             "select_elements": ["Deposit", "Withdrawal"], "listing": True}
        ]
    }
]

for entity in entities:
    generate_entity(**entity)

print(f"Generated {len(entities)} configurations under {base_dir}")
