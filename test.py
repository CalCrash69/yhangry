import unittest
from unittest.mock import patch, Mock
from main import ApolloLeadSearch


class TestApolloLeadSearch(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.lead_searcher = ApolloLeadSearch(self.api_key)

        # Mock API response data
        self.mock_response_data = {
            "people": [
                {
                    "first_name": "Gordon",
                    "last_name": "Ramsay",
                    "email": "gordon@hellskitchen.com",
                    "title": "Executive Chef",
                    "organization": {"name": "Hell's Kitchen"},
                    "linkedin_url": "linkedin.com/in/gordonramsay",
                },
                {
                    "first_name": "Wolfgang",
                    "last_name": "Puck",
                    "email": "wolfgang@spago.com",
                    "title": "Head Chef",
                    "organization": {"name": "Spago"},
                    "linkedin_url": "linkedin.com/in/wolfgangpuck",
                },
                {
                    "first_name": "Alain",
                    "last_name": "Ducasse",
                    "email": "alain@ducasse.com",
                    "title": "Chef",
                    "organization": {"name": "Alain Ducasse Enterprises"},
                    "linkedin_url": "linkedin.com/in/alainducasse",
                },
            ],
            "pagination": {"total_entries": 3, "total_pages": 1},
        }

    @patch("requests.post")
    def test_search_people(self, mock_post):
        # Configure mock
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_post.return_value = mock_response

        # Test the search_people method
        result = self.lead_searcher.search_people(page=1)

        # Verify the API was called with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(
            call_args[1]["headers"]["Authorization"], f"Bearer {self.api_key}"
        )

        # Verify the response contains expected data
        self.assertEqual(len(result["people"]), 3)
        self.assertEqual(result["people"][0]["first_name"], "Gordon")

    def test_extract_lead_info(self):
        # Test lead information extraction
        leads = self.lead_searcher.extract_lead_info(self.mock_response_data["people"])

        # Verify extracted data
        self.assertEqual(len(leads), 3)

        # Check first lead
        first_lead = leads[0]
        self.assertEqual(first_lead["name"], "Gordon Ramsay")
        self.assertEqual(first_lead["email"], "gordon@hellskitchen.com")
        self.assertEqual(first_lead["title"], "Executive Chef")
        self.assertEqual(first_lead["company"], "Hell's Kitchen")
        self.assertEqual(first_lead["linkedin_url"], "linkedin.com/in/gordonramsay")

    @patch("requests.post")
    def test_search_and_save_leads(self, mock_post):
        # Configure mock
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_post.return_value = mock_response

        # Test with temp file
        test_output_file = "test_chef_leads.csv"

        # Run the search and save
        df = self.lead_searcher.search_and_save_leads(
            num_pages=1, output_file=test_output_file
        )

        # Verify results
        self.assertEqual(len(df), 3)
        self.assertTrue("name" in df.columns)
        self.assertTrue("email" in df.columns)
        self.assertTrue("title" in df.columns)

        # Verify first row
        first_row = df.iloc[0]
        self.assertEqual(first_row["name"], "Gordon Ramsay")
        self.assertEqual(first_row["email"], "gordon@hellskitchen.com")

    def test_missing_data_handling(self):
        # Test with incomplete data
        incomplete_data = [
            {
                "first_name": "Unknown",
                "last_name": "Chef",
                # Missing email and other fields
            }
        ]

        leads = self.lead_searcher.extract_lead_info(incomplete_data)

        # Verify default values are used for missing data
        self.assertEqual(leads[0]["email"], "Not available")
        self.assertEqual(leads[0]["title"], "Not available")
        self.assertEqual(leads[0]["company"], "Not available")


if __name__ == "__main__":
    unittest.main()
