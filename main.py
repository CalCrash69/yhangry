import requests
import pandas as pd
from typing import List, Dict


class ApolloLeadSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Authorization": f"Bearer {self.api_key}",
        }

    def search_people(self, page: int = 1, per_page: int = 100) -> Dict:
        """
        Search for people with chef titles using Apollo.io API
        """
        endpoint = f"{self.base_url}/mixed_people/search"

        payload = {
            "api_key": self.api_key,
            "q_keywords": "chef",
            "page": page,
            "per_page": per_page,
            "person_titles": [
                "Chef",
                "Head Chef",
                "Executive Chef",
                "Sous Chef",
                "Pastry Chef",
            ],
        }

        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()

    def extract_lead_info(self, people: List[Dict]) -> List[Dict]:
        """
        Extract relevant information from the API response
        """
        leads = []
        for person in people:
            lead = {
                "name": f"{person.get('first_name', '')} {person.get('last_name', '')}",
                "email": person.get("email", "Not available"),
                "title": person.get("title", "Not available"),
                "company": person.get("organization", {}).get("name", "Not available"),
                "linkedin_url": person.get("linkedin_url", "Not available"),
            }
            leads.append(lead)
        return leads

    def search_and_save_leads(
        self, num_pages: int = 5, output_file: str = "chef_leads.csv"
    ):
        """
        Search for leads across multiple pages and save to CSV
        """
        all_leads = []

        for page in range(1, num_pages + 1):
            print(f"Processing page {page}...")

            response = self.search_people(page=page)

            if response.get("people"):
                leads = self.extract_lead_info(response["people"])
                all_leads.extend(leads)

        # Convert to DataFrame and save
        df = pd.DataFrame(all_leads)
        df.to_csv(output_file, index=False)
        print(f"Saved {len(all_leads)} leads to {output_file}")
        return df
