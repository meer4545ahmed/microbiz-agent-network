"""Credential input guard tests; fixtures are fake and nonfunctional."""

import unittest

from microbiz.security import contains_credential, requests_live_store_connection


class CredentialGuardTests(unittest.TestCase):
    def test_detects_shopify_style_token(self) -> None:
        self.assertTrue(contains_credential("please use shpat_" + "A" * 32))

    def test_detects_bearer_token(self) -> None:
        self.assertTrue(contains_credential("Authorization: Bearer " + "xY9" * 12))

    def test_detects_labeled_api_key(self) -> None:
        self.assertTrue(contains_credential("api_key=" + "aB3" * 8))

    def test_allows_normal_operations_request(self) -> None:
        self.assertFalse(
            contains_credential(
                "Review today's orders and inventory, identify problems, and prepare drafts."
            )
        )

    def test_does_not_flag_explicit_placeholder(self) -> None:
        self.assertFalse(contains_credential("api_key=YOUR_API_KEY_HERE"))

    def test_shopify_request_is_routed_to_secure_connection_explanation(self) -> None:
        self.assertTrue(requests_live_store_connection("Connect my Shopify store"))

    def test_regular_inventory_request_is_not_a_connection_request(self) -> None:
        self.assertFalse(requests_live_store_connection("Review today's inventory"))


if __name__ == "__main__":
    unittest.main()
