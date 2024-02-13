import os
import requests
from bs4 import BeautifulSoup
import json

def get_vote_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve data from the URL:", url)
        return None

    soup = BeautifulSoup(response.content, "xml")
    vote_data = {}
    
    # Extract metadata
    metadata_tags = ["congress", "session", "congress_year", "vote_number", "vote_date", "modify_date",
                     "vote_question_text", "vote_document_text", "vote_result_text", "question", "vote_title",
                     "majority_requirement", "vote_result"]
    for tag in metadata_tags:
        vote_data[tag] = soup.find(tag).get_text() if soup.find(tag) else ""

    # Extract document data
    document_data = {}
    document_tags = ["document_congress", "document_type", "document_number", "document_name", "document_title",
                     "document_short_title"]
    for tag in document_tags:
        document_data[tag] = soup.find(tag).get_text() if soup.find(tag) else ""
    vote_data["document"] = document_data

    # Extract count data
    count_data = {}
    count_tags = ["yeas", "nays", "present", "absent"]
    for tag in count_tags:
        count_data[tag] = soup.find(tag).get_text() if soup.find(tag) else ""
    vote_data["count"] = count_data

    # Extract individual votes
    member_tags = soup.find_all("member")
    individual_votes = []
    for member in member_tags:
        member_data = {}
        member_data["member_full"] = member.find("member_full").get_text() if member.find("member_full") else ""
        member_data["last_name"] = member.find("last_name").get_text() if member.find("last_name") else ""
        member_data["first_name"] = member.find("first_name").get_text() if member.find("first_name") else ""
        member_data["party"] = member.find("party").get_text() if member.find("party") else ""
        member_data["state"] = member.find("state").get_text() if member.find("state") else ""
        member_data["vote_cast"] = member.find("vote_cast").get_text() if member.find("vote_cast") else ""
        member_data["lis_member_id"] = member.find("lis_member_id").get_text() if member.find("lis_member_id") else ""
        individual_votes.append(member_data)
    vote_data["members"] = individual_votes

    return vote_data

def save_to_json(filename, vote_data):
    with open(filename, "w", encoding="utf-8") as jsonfile:
        json.dump(vote_data, jsonfile, indent=4)

def main():
    base_url = "https://www.senate.gov/legislative/LIS/roll_call_votes/vote1182/vote_118_2_"
    start_vote_number = 43
    max_votes = 10  # Number of votes to fetch
    
    for i in range(start_vote_number, start_vote_number + max_votes):
        url = f"{base_url}{i:05d}.xml"
        vote_data = get_vote_data(url)
        if vote_data:
            filename_json = f"senate_{vote_data['vote_number']}_{vote_data['vote_date'].replace(',', '').replace(':', '').replace(' ', '_')}.json"
            if not os.path.exists(filename_json):
                save_to_json(filename_json, vote_data)
                print(f"Saved data to {filename_json}")
            else:
                print(f"Data already exists for vote {vote_data['vote_number']}")

if __name__ == "__main__":
    main()
