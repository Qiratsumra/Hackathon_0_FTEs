# 🧾 Create Draft Odoo Invoice Skill

## Purpose
This skill allows the AI Employee to create a draft customer invoice in Odoo, based on provided customer and product details. This is typically used for generating invoices that require review or further processing before being sent to the customer.

## Input Parameters
The AI Employee needs the following information to create a draft invoice:

1.  **`partner_name` (string, required):** The full name of the customer for whom the invoice is to be created. The AI will attempt to find an existing partner in Odoo based on this name. If multiple matches or no matches are found, it should prompt for clarification or partner ID.
2.  **`product_details` (list of objects, required):** A list describing the items to be included in the invoice. Each object in the list should contain:
    *   `product_name` (string, required): The name of the product or service. The AI will search for this product in Odoo.
    *   `quantity` (number, required): The quantity of the product/service.
    *   `price_unit` (number, optional): The unit price of the product/service. If not provided, Odoo's default list price for the product will be used.
3.  **`currency` (string, optional):** The 3-letter currency code (e.g., "USD", "EUR"). If not provided, Odoo's default currency will be used.
4.  **`invoice_date` (string, optional):** The date of the invoice in 'YYYY-MM-DD' format. If not provided, the current date will be used.

## Output
Upon successful creation of a draft invoice, the skill will return:
-   `success` (boolean): `true` if the invoice was created, `false` otherwise.
-   `invoice_id` (integer): The unique ID of the newly created draft invoice in Odoo.
-   `invoice_name` (string): The reference name or number of the draft invoice.
-   `message` (string): A descriptive message about the outcome.

If the skill fails, it will return:
-   `success` (boolean): `false`.
-   `message` (string): An error message explaining the failure (e.g., "Customer not found", "Product not found", "Connection error").

## Execution Steps (Internal AI Logic)
1.  **Find Customer:** Use `odoo-mcp.get_partners` to search for `partner_name`. If found, extract `partner_id`. If not unique, ask for clarification.
2.  **Find Products:** For each item in `product_details`, use `odoo-mcp.search_products` to find the `product_id`. If not found or not unique, ask for clarification.
3.  **Prepare Product Lines:** Format `product_details` into the structure expected by `odoo_mcp.create_invoice_draft` (i.e., `product_id`, `quantity`, `price_unit`).
4.  **Create Invoice:** Invoke `odoo-mcp.create_invoice_draft` with the gathered `partner_id`, formatted `product_lines`, and optional `currency_id` (after mapping `currency` string to Odoo ID if provided) and `invoice_date`.
5.  **Report Result:** Log the outcome and present the `invoice_id` and `invoice_name` if successful.

## Example Usage (AI thought process)

**User Request:** "Please create a draft invoice for John Doe for 2 hours of consulting at $150/hour."

**AI Reasoning:**
1.  **Identify Skill:** User wants to create an invoice, so `create_draft_invoice` skill is relevant.
2.  **Extract Parameters:**
    *   `partner_name`: "John Doe"
    *   `product_details`: `[{'product_name': 'Consulting', 'quantity': 2, 'price_unit': 150}]`
3.  **Find Customer (MCP Call):** `odoo-mcp.get_partners(domain=[['name', 'ilike', 'John Doe']], fields=['id', 'name'])`
    *   *Result:* `[{'id': 123, 'name': 'John Doe'}]` -> `partner_id = 123`
4.  **Find Product (MCP Call):** `odoo-mcp.search_products(name='Consulting')`
    *   *Result:* `[{'id': 456, 'name': 'Consulting Services', 'list_price': 100.0}]` -> `product_id = 456`
5.  **Create Invoice (MCP Call):** `odoo-mcp.create_invoice_draft(partner_id=123, product_lines=[{'product_id': 456, 'quantity': 2, 'price_unit': 150.0}])`
    *   *Result:* `{'success': true, 'invoice_id': 789, 'invoice_name': 'INV/2026/00001'}`
6.  **Respond to User:** "I have successfully created a draft invoice (INV/2026/00001) for John Doe in Odoo. The invoice ID is 789."

## Security & Approval Considerations
-   This skill creates a *draft* invoice, which does not immediately affect finances.
-   Any action to *validate* or *send* an invoice should be handled by a separate skill, likely requiring human approval (e.g., using `approval_creator` for financial transactions).
-   All Odoo interactions are logged by the `odoo_mcp`.
