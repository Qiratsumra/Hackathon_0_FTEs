import os
import logging
import odoorpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OdooMCP:
    def __init__(self):
        self.ODOO_HOST = os.getenv("ODOO_HOST")
        self.ODOO_PORT = int(os.getenv("ODOO_PORT", 8069))
        self.DB_NAME = os.getenv("ODOO_DB_NAME")
        self.USERNAME = os.getenv("ODOO_USERNAME")
        self.PASSWORD = os.getenv("ODOO_PASSWORD")

        self.odoo = None

        if not all([self.ODOO_HOST, self.DB_NAME, self.USERNAME, self.PASSWORD]):
            logger.error("Missing required Odoo environment variables.")
            raise ValueError("Missing Odoo configuration environment variables.")

        self._connect()

    def _connect(self):
        """Establish connection to Odoo via XML-RPC."""
        try:
            logger.info(
                f"Connecting to Odoo at {self.ODOO_HOST}:{self.ODOO_PORT} "
                f"(DB: {self.DB_NAME})"
            )

            self.odoo = odoorpc.ODOO(
                host=self.ODOO_HOST,
                port=self.ODOO_PORT,
            )

            self.odoo.login(
                db=self.DB_NAME,
                login=self.USERNAME,
                password=self.PASSWORD,
            )

            logger.info("Successfully connected to Odoo.")

        except Exception as e:
            logger.error(f"Odoo connection failed: {e}")
            self.odoo = None
            raise

    # -------------------------
    # Business Operations
    # -------------------------

    def get_partners(self, domain=None, fields=None, limit=None):
        if not self.odoo:
            raise ConnectionError("Not connected to Odoo.")

        domain = domain or []
        fields = fields or ["id", "name", "email"]

        try:
            logger.info("Fetching partners")
            Partner = self.odoo.env["res.partner"]
            return Partner.search_read(domain, fields, limit=limit)
        except Exception as e:
            logger.error(f"Failed to fetch partners: {e}")
            return []

    def search_products(self, name=None, limit=None):
        if not self.odoo:
            raise ConnectionError("Not connected to Odoo.")

        domain = []
        if name:
            domain.append(("name", "ilike", name))

        fields = ["id", "name", "list_price"]

        try:
            logger.info(f"Searching products: {name}")
            Product = self.odoo.env["product.product"]
            return Product.search_read(domain, fields, limit=limit)
        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            return []

    def create_invoice_draft(
        self,
        partner_id: int,
        product_lines: list,
        currency_id: int | None = None,
        date_invoice: str | None = None,
    ):
        if not self.odoo:
            raise ConnectionError("Not connected to Odoo.")

        try:
            logger.info(f"Creating draft invoice for partner {partner_id}")

            Move = self.odoo.env["account.move"]

            invoice_vals = {
                "partner_id": partner_id,
                "move_type": "out_invoice",
                "invoice_line_ids": [],
            }

            if currency_id:
                invoice_vals["currency_id"] = currency_id
            if date_invoice:
                invoice_vals["invoice_date"] = date_invoice

            for line in product_lines:
                invoice_vals["invoice_line_ids"].append(
                    (
                        0,
                        0,
                        {
                            "product_id": line["product_id"],
                            "quantity": line["quantity"],
                            "price_unit": line["price_unit"],
                        },
                    )
                )

            invoice_id = Move.create(invoice_vals)

            invoice = Move.browse(invoice_id)

            logger.info(f"Draft invoice created: ID={invoice.id}")

            return {
                "success": True,
                "invoice_id": invoice.id,
                "invoice_name": invoice.name,
            }

        except Exception as e:
            logger.error(f"Invoice creation failed: {e}")
            return {"success": False, "message": str(e)}


if __name__ == "__main__":
    try:
        odoo_mcp = OdooMCP()

        print("\n--- Partners ---")
        for p in odoo_mcp.get_partners(limit=5):
            print(f"{p['id']} - {p['name']}")

        print("\n--- Products ---")
        for prod in odoo_mcp.search_products(name="desk", limit=3):
            print(f"{prod['id']} - {prod['name']} - {prod['list_price']}")

    except Exception as e:
        print(f"Startup failed: {e}")
