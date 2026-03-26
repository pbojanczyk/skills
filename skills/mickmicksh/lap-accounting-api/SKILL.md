---
name: lap-accounting-api
description: "Accounting API skill. Use when working with Accounting for accounting. Covers 143 endpoints."
version: 1.0.0
generator: lapsh
metadata:
  openclaw:
    requires:
      env:
        - ACCOUNTING_API_KEY
---

# Accounting API
API version: 10.24.7

## Auth
ApiKey Authorization in header

## Base URL
https://unify.apideck.com

## Setup
1. Set your API key in the appropriate header
2. GET /accounting/tax-rates -- verify access
3. POST /accounting/tax-rates -- create first tax-rates

## Endpoints

143 endpoints across 1 groups. See references/api-spec.lap for full details.

### accounting
| Method | Path | Description |
|--------|------|-------------|
| GET | /accounting/tax-rates | List Tax Rates |
| POST | /accounting/tax-rates | Create Tax Rate |
| GET | /accounting/tax-rates/{id} | Get Tax Rate |
| PATCH | /accounting/tax-rates/{id} | Update Tax Rate |
| DELETE | /accounting/tax-rates/{id} | Delete Tax Rate |
| GET | /accounting/bills | List Bills |
| POST | /accounting/bills | Create Bill |
| GET | /accounting/bills/{id} | Get Bill |
| PATCH | /accounting/bills/{id} | Update Bill |
| DELETE | /accounting/bills/{id} | Delete Bill |
| GET | /accounting/invoices | List Invoices |
| POST | /accounting/invoices | Create Invoice |
| GET | /accounting/invoices/{id} | Get Invoice |
| PATCH | /accounting/invoices/{id} | Update Invoice |
| DELETE | /accounting/invoices/{id} | Delete Invoice |
| GET | /accounting/ledger-accounts | List Ledger Accounts |
| POST | /accounting/ledger-accounts | Create Ledger Account |
| GET | /accounting/ledger-accounts/{id} | Get Ledger Account |
| PATCH | /accounting/ledger-accounts/{id} | Update Ledger Account |
| DELETE | /accounting/ledger-accounts/{id} | Delete Ledger Account |
| GET | /accounting/invoice-items | List Invoice Items |
| POST | /accounting/invoice-items | Create Invoice Item |
| GET | /accounting/invoice-items/{id} | Get Invoice Item |
| PATCH | /accounting/invoice-items/{id} | Update Invoice Item |
| DELETE | /accounting/invoice-items/{id} | Delete Invoice Item |
| GET | /accounting/credit-notes | List Credit Notes |
| POST | /accounting/credit-notes | Create Credit Note |
| GET | /accounting/credit-notes/{id} | Get Credit Note |
| PATCH | /accounting/credit-notes/{id} | Update Credit Note |
| DELETE | /accounting/credit-notes/{id} | Delete Credit Note |
| GET | /accounting/customers | List Customers |
| POST | /accounting/customers | Create Customer |
| GET | /accounting/customers/{id} | Get Customer |
| PATCH | /accounting/customers/{id} | Update Customer |
| DELETE | /accounting/customers/{id} | Delete Customer |
| GET | /accounting/suppliers | List Suppliers |
| POST | /accounting/suppliers | Create Supplier |
| GET | /accounting/suppliers/{id} | Get Supplier |
| PATCH | /accounting/suppliers/{id} | Update Supplier |
| DELETE | /accounting/suppliers/{id} | Delete Supplier |
| GET | /accounting/payments | List Payments |
| POST | /accounting/payments | Create Payment |
| GET | /accounting/payments/{id} | Get Payment |
| PATCH | /accounting/payments/{id} | Update Payment |
| DELETE | /accounting/payments/{id} | Delete Payment |
| GET | /accounting/refunds | List Refunds |
| POST | /accounting/refunds | Create Refund |
| GET | /accounting/refunds/{id} | Get Refund |
| PATCH | /accounting/refunds/{id} | Update Refund |
| DELETE | /accounting/refunds/{id} | Delete Refund |
| GET | /accounting/company-info | Get company info |
| GET | /accounting/companies | List companies |
| GET | /accounting/balance-sheet | Get BalanceSheet |
| GET | /accounting/profit-and-loss | Get Profit and Loss |
| GET | /accounting/journal-entries | List Journal Entries |
| POST | /accounting/journal-entries | Create Journal Entry |
| GET | /accounting/journal-entries/{id} | Get Journal Entry |
| PATCH | /accounting/journal-entries/{id} | Update Journal Entry |
| DELETE | /accounting/journal-entries/{id} | Delete Journal Entry |
| GET | /accounting/purchase-orders | List Purchase Orders |
| POST | /accounting/purchase-orders | Create Purchase Order |
| GET | /accounting/purchase-orders/{id} | Get Purchase Order |
| PATCH | /accounting/purchase-orders/{id} | Update Purchase Order |
| DELETE | /accounting/purchase-orders/{id} | Delete Purchase Order |
| GET | /accounting/subsidiaries | List Subsidiaries |
| POST | /accounting/subsidiaries | Create Subsidiary |
| GET | /accounting/subsidiaries/{id} | Get Subsidiary |
| PATCH | /accounting/subsidiaries/{id} | Update Subsidiary |
| DELETE | /accounting/subsidiaries/{id} | Delete Subsidiary |
| GET | /accounting/locations | List Locations |
| POST | /accounting/locations | Create Location |
| GET | /accounting/locations/{id} | Get Location |
| PATCH | /accounting/locations/{id} | Update Location |
| DELETE | /accounting/locations/{id} | Delete Location |
| GET | /accounting/departments | List Departments |
| POST | /accounting/departments | Create Department |
| GET | /accounting/departments/{id} | Get Department |
| PATCH | /accounting/departments/{id} | Update Department |
| DELETE | /accounting/departments/{id} | Delete Department |
| GET | /accounting/attachments/{reference_type}/{reference_id} | List Attachments |
| POST | /accounting/attachments/{reference_type}/{reference_id} | Upload attachment |
| GET | /accounting/attachments/{reference_type}/{reference_id}/{id} | Get Attachment |
| DELETE | /accounting/attachments/{reference_type}/{reference_id}/{id} | Delete Attachment |
| GET | /accounting/attachments/{reference_type}/{reference_id}/{id}/download | Download Attachment |
| GET | /accounting/bank-accounts | List Bank Accounts |
| POST | /accounting/bank-accounts | Create Bank Account |
| GET | /accounting/bank-accounts/{id} | Get Bank Account |
| PATCH | /accounting/bank-accounts/{id} | Update Bank Account |
| DELETE | /accounting/bank-accounts/{id} | Delete Bank Account |
| GET | /accounting/tracking-categories | List Tracking Categories |
| POST | /accounting/tracking-categories | Create Tracking Category |
| GET | /accounting/tracking-categories/{id} | Get Tracking Category |
| PATCH | /accounting/tracking-categories/{id} | Update Tracking Category |
| DELETE | /accounting/tracking-categories/{id} | Delete Tracking Category |
| GET | /accounting/bill-payments | List Bill Payments |
| POST | /accounting/bill-payments | Create Bill Payment |
| GET | /accounting/bill-payments/{id} | Get Bill Payment |
| PATCH | /accounting/bill-payments/{id} | Update Bill Payment |
| DELETE | /accounting/bill-payments/{id} | Delete Bill Payment |
| GET | /accounting/expenses | List Expenses |
| POST | /accounting/expenses | Create Expense |
| GET | /accounting/expenses/{id} | Get Expense |
| PATCH | /accounting/expenses/{id} | Update Expense |
| DELETE | /accounting/expenses/{id} | Delete Expense |
| GET | /accounting/aged-creditors | Get Aged Creditors |
| GET | /accounting/aged-debtors | Get Aged Debtors |
| GET | /accounting/bank-feed-accounts | List Bank Feed Accounts |
| POST | /accounting/bank-feed-accounts | Create Bank Feed Account |
| GET | /accounting/bank-feed-accounts/{id} | Get Bank Feed Account |
| PATCH | /accounting/bank-feed-accounts/{id} | Update Bank Feed Account |
| DELETE | /accounting/bank-feed-accounts/{id} | Delete Bank Feed Account |
| GET | /accounting/bank-feed-statements | List Bank Feed Statements |
| POST | /accounting/bank-feed-statements | Create Bank Feed Statement |
| GET | /accounting/bank-feed-statements/{id} | Get Bank Feed Statement |
| PATCH | /accounting/bank-feed-statements/{id} | Update Bank Feed Statement |
| DELETE | /accounting/bank-feed-statements/{id} | Delete Bank Feed Statement |
| GET | /accounting/categories | List Categories |
| GET | /accounting/categories/{id} | Get Category |
| GET | /accounting/quotes | List Quotes |
| POST | /accounting/quotes | Create Quote |
| GET | /accounting/quotes/{id} | Get Quote |
| PATCH | /accounting/quotes/{id} | Update Quote |
| DELETE | /accounting/quotes/{id} | Delete Quote |
| GET | /accounting/projects | List projects |
| POST | /accounting/projects | Create project |
| GET | /accounting/projects/{id} | Get project |
| PATCH | /accounting/projects/{id} | Update project |
| DELETE | /accounting/projects/{id} | Delete project |
| GET | /accounting/employees | List Employees |
| POST | /accounting/employees | Create Employee |
| GET | /accounting/employees/{id} | Get Employee |
| PATCH | /accounting/employees/{id} | Update Employee |
| DELETE | /accounting/employees/{id} | Delete Employee |
| GET | /accounting/expense-categories | List Expense Categories |
| POST | /accounting/expense-categories | Create Expense Category |
| GET | /accounting/expense-categories/{id} | Get Expense Category |
| PATCH | /accounting/expense-categories/{id} | Update Expense Category |
| DELETE | /accounting/expense-categories/{id} | Delete Expense Category |
| GET | /accounting/expense-reports | List Expense Reports |
| POST | /accounting/expense-reports | Create Expense Report |
| GET | /accounting/expense-reports/{id} | Get Expense Report |
| PATCH | /accounting/expense-reports/{id} | Update Expense Report |
| DELETE | /accounting/expense-reports/{id} | Delete Expense Report |

## Common Questions

Match user requests to endpoints in references/api-spec.lap. Key patterns:
- "List all tax-rates?" -> GET /accounting/tax-rates
- "Create a tax-rate?" -> POST /accounting/tax-rates
- "Get tax-rate details?" -> GET /accounting/tax-rates/{id}
- "Partially update a tax-rate?" -> PATCH /accounting/tax-rates/{id}
- "Delete a tax-rate?" -> DELETE /accounting/tax-rates/{id}
- "List all bills?" -> GET /accounting/bills
- "Create a bill?" -> POST /accounting/bills
- "Get bill details?" -> GET /accounting/bills/{id}
- "Partially update a bill?" -> PATCH /accounting/bills/{id}
- "Delete a bill?" -> DELETE /accounting/bills/{id}
- "List all invoices?" -> GET /accounting/invoices
- "Create a invoice?" -> POST /accounting/invoices
- "Get invoice details?" -> GET /accounting/invoices/{id}
- "Partially update a invoice?" -> PATCH /accounting/invoices/{id}
- "Delete a invoice?" -> DELETE /accounting/invoices/{id}
- "List all ledger-accounts?" -> GET /accounting/ledger-accounts
- "Create a ledger-account?" -> POST /accounting/ledger-accounts
- "Get ledger-account details?" -> GET /accounting/ledger-accounts/{id}
- "Partially update a ledger-account?" -> PATCH /accounting/ledger-accounts/{id}
- "Delete a ledger-account?" -> DELETE /accounting/ledger-accounts/{id}
- "List all invoice-items?" -> GET /accounting/invoice-items
- "Create a invoice-item?" -> POST /accounting/invoice-items
- "Get invoice-item details?" -> GET /accounting/invoice-items/{id}
- "Partially update a invoice-item?" -> PATCH /accounting/invoice-items/{id}
- "Delete a invoice-item?" -> DELETE /accounting/invoice-items/{id}
- "List all credit-notes?" -> GET /accounting/credit-notes
- "Create a credit-note?" -> POST /accounting/credit-notes
- "Get credit-note details?" -> GET /accounting/credit-notes/{id}
- "Partially update a credit-note?" -> PATCH /accounting/credit-notes/{id}
- "Delete a credit-note?" -> DELETE /accounting/credit-notes/{id}
- "List all customers?" -> GET /accounting/customers
- "Create a customer?" -> POST /accounting/customers
- "Get customer details?" -> GET /accounting/customers/{id}
- "Partially update a customer?" -> PATCH /accounting/customers/{id}
- "Delete a customer?" -> DELETE /accounting/customers/{id}
- "List all suppliers?" -> GET /accounting/suppliers
- "Create a supplier?" -> POST /accounting/suppliers
- "Get supplier details?" -> GET /accounting/suppliers/{id}
- "Partially update a supplier?" -> PATCH /accounting/suppliers/{id}
- "Delete a supplier?" -> DELETE /accounting/suppliers/{id}
- "List all payments?" -> GET /accounting/payments
- "Create a payment?" -> POST /accounting/payments
- "Get payment details?" -> GET /accounting/payments/{id}
- "Partially update a payment?" -> PATCH /accounting/payments/{id}
- "Delete a payment?" -> DELETE /accounting/payments/{id}
- "List all refunds?" -> GET /accounting/refunds
- "Create a refund?" -> POST /accounting/refunds
- "Get refund details?" -> GET /accounting/refunds/{id}
- "Partially update a refund?" -> PATCH /accounting/refunds/{id}
- "Delete a refund?" -> DELETE /accounting/refunds/{id}
- "List all company-info?" -> GET /accounting/company-info
- "List all companies?" -> GET /accounting/companies
- "List all balance-sheet?" -> GET /accounting/balance-sheet
- "List all profit-and-loss?" -> GET /accounting/profit-and-loss
- "List all journal-entries?" -> GET /accounting/journal-entries
- "Create a journal-entry?" -> POST /accounting/journal-entries
- "Get journal-entry details?" -> GET /accounting/journal-entries/{id}
- "Partially update a journal-entry?" -> PATCH /accounting/journal-entries/{id}
- "Delete a journal-entry?" -> DELETE /accounting/journal-entries/{id}
- "List all purchase-orders?" -> GET /accounting/purchase-orders
- "Create a purchase-order?" -> POST /accounting/purchase-orders
- "Get purchase-order details?" -> GET /accounting/purchase-orders/{id}
- "Partially update a purchase-order?" -> PATCH /accounting/purchase-orders/{id}
- "Delete a purchase-order?" -> DELETE /accounting/purchase-orders/{id}
- "List all subsidiaries?" -> GET /accounting/subsidiaries
- "Create a subsidiary?" -> POST /accounting/subsidiaries
- "Get subsidiary details?" -> GET /accounting/subsidiaries/{id}
- "Partially update a subsidiary?" -> PATCH /accounting/subsidiaries/{id}
- "Delete a subsidiary?" -> DELETE /accounting/subsidiaries/{id}
- "List all locations?" -> GET /accounting/locations
- "Create a location?" -> POST /accounting/locations
- "Get location details?" -> GET /accounting/locations/{id}
- "Partially update a location?" -> PATCH /accounting/locations/{id}
- "Delete a location?" -> DELETE /accounting/locations/{id}
- "List all departments?" -> GET /accounting/departments
- "Create a department?" -> POST /accounting/departments
- "Get department details?" -> GET /accounting/departments/{id}
- "Partially update a department?" -> PATCH /accounting/departments/{id}
- "Delete a department?" -> DELETE /accounting/departments/{id}
- "Get attachment details?" -> GET /accounting/attachments/{reference_type}/{reference_id}
- "Get attachment details?" -> GET /accounting/attachments/{reference_type}/{reference_id}/{id}
- "Delete a attachment?" -> DELETE /accounting/attachments/{reference_type}/{reference_id}/{id}
- "List all download?" -> GET /accounting/attachments/{reference_type}/{reference_id}/{id}/download
- "List all bank-accounts?" -> GET /accounting/bank-accounts
- "Create a bank-account?" -> POST /accounting/bank-accounts
- "Get bank-account details?" -> GET /accounting/bank-accounts/{id}
- "Partially update a bank-account?" -> PATCH /accounting/bank-accounts/{id}
- "Delete a bank-account?" -> DELETE /accounting/bank-accounts/{id}
- "List all tracking-categories?" -> GET /accounting/tracking-categories
- "Create a tracking-category?" -> POST /accounting/tracking-categories
- "Get tracking-category details?" -> GET /accounting/tracking-categories/{id}
- "Partially update a tracking-category?" -> PATCH /accounting/tracking-categories/{id}
- "Delete a tracking-category?" -> DELETE /accounting/tracking-categories/{id}
- "List all bill-payments?" -> GET /accounting/bill-payments
- "Create a bill-payment?" -> POST /accounting/bill-payments
- "Get bill-payment details?" -> GET /accounting/bill-payments/{id}
- "Partially update a bill-payment?" -> PATCH /accounting/bill-payments/{id}
- "Delete a bill-payment?" -> DELETE /accounting/bill-payments/{id}
- "List all expenses?" -> GET /accounting/expenses
- "Create a expense?" -> POST /accounting/expenses
- "Get expense details?" -> GET /accounting/expenses/{id}
- "Partially update a expense?" -> PATCH /accounting/expenses/{id}
- "Delete a expense?" -> DELETE /accounting/expenses/{id}
- "List all aged-creditors?" -> GET /accounting/aged-creditors
- "List all aged-debtors?" -> GET /accounting/aged-debtors
- "List all bank-feed-accounts?" -> GET /accounting/bank-feed-accounts
- "Create a bank-feed-account?" -> POST /accounting/bank-feed-accounts
- "Get bank-feed-account details?" -> GET /accounting/bank-feed-accounts/{id}
- "Partially update a bank-feed-account?" -> PATCH /accounting/bank-feed-accounts/{id}
- "Delete a bank-feed-account?" -> DELETE /accounting/bank-feed-accounts/{id}
- "List all bank-feed-statements?" -> GET /accounting/bank-feed-statements
- "Create a bank-feed-statement?" -> POST /accounting/bank-feed-statements
- "Get bank-feed-statement details?" -> GET /accounting/bank-feed-statements/{id}
- "Partially update a bank-feed-statement?" -> PATCH /accounting/bank-feed-statements/{id}
- "Delete a bank-feed-statement?" -> DELETE /accounting/bank-feed-statements/{id}
- "List all categories?" -> GET /accounting/categories
- "Get category details?" -> GET /accounting/categories/{id}
- "List all quotes?" -> GET /accounting/quotes
- "Create a quote?" -> POST /accounting/quotes
- "Get quote details?" -> GET /accounting/quotes/{id}
- "Partially update a quote?" -> PATCH /accounting/quotes/{id}
- "Delete a quote?" -> DELETE /accounting/quotes/{id}
- "List all projects?" -> GET /accounting/projects
- "Create a project?" -> POST /accounting/projects
- "Get project details?" -> GET /accounting/projects/{id}
- "Partially update a project?" -> PATCH /accounting/projects/{id}
- "Delete a project?" -> DELETE /accounting/projects/{id}
- "List all employees?" -> GET /accounting/employees
- "Create a employee?" -> POST /accounting/employees
- "Get employee details?" -> GET /accounting/employees/{id}
- "Partially update a employee?" -> PATCH /accounting/employees/{id}
- "Delete a employee?" -> DELETE /accounting/employees/{id}
- "List all expense-categories?" -> GET /accounting/expense-categories
- "Create a expense-category?" -> POST /accounting/expense-categories
- "Get expense-category details?" -> GET /accounting/expense-categories/{id}
- "Partially update a expense-category?" -> PATCH /accounting/expense-categories/{id}
- "Delete a expense-category?" -> DELETE /accounting/expense-categories/{id}
- "List all expense-reports?" -> GET /accounting/expense-reports
- "Create a expense-report?" -> POST /accounting/expense-reports
- "Get expense-report details?" -> GET /accounting/expense-reports/{id}
- "Partially update a expense-report?" -> PATCH /accounting/expense-reports/{id}
- "Delete a expense-report?" -> DELETE /accounting/expense-reports/{id}
- "How to authenticate?" -> See Auth section

## Response Tips
- Check response schemas in references/api-spec.lap for field details
- List endpoints may support pagination; check for limit, offset, or cursor params
- Create/update endpoints typically return the created/updated object

## CLI

```bash
# Update this spec to the latest version
npx @lap-platform/lapsh get accounting-api -o references/api-spec.lap

# Search for related APIs
npx @lap-platform/lapsh search accounting-api
```

## References
- Full spec: See references/api-spec.lap for complete endpoint details, parameter tables, and response schemas

> Generated from the official API spec by [LAP](https://lap.sh)
