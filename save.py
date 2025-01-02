import requests
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm

# Function to process the title and determine the file extension
def process_title(title):
    """Process the title to clean and determine the appropriate file extension."""
    if "– HUBLinks" in title:
        title = title.replace("– HUBLinks", " ")
    
    if any(season in title.lower() for season in [f"s{i:02d}" for i in range(1, 14)]):
        return title, ".zip"
    else:
        return title, ".mkv"

# Function to clean file name
def clean_file_name(file_name):
    """Remove unwanted characters from the file name."""
    return file_name.replace('(', '').replace(')', '').strip()

# Function to get the title of a webpage
def get_title(url):
    """Fetch the webpage title and return the processed title and its extension."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return process_title(soup.title.string)
        else:
            print(f"Failed to retrieve {url}: Status code {response.status_code}")
            return None, None
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return None, None

# Function to append a new entry to the JSON file
def append_to_json(file_path, data):
    """Append a new entry to the JSON file."""
    # If the file doesn't exist, create it with a JSON array
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("[\n")
    
    with open(file_path, "a") as f:
        if os.path.getsize(file_path) > 2:  # Check if file is not empty
            f.write(",\n")  # Add a comma for formatting
        json.dump(data, f, ensure_ascii=False, indent=2)

# Function to update the progress file
def update_progress(progress_file, last_processed, start_number, end_number):
    """Update the progress file with the last processed information."""
    progress_data = {
        "last_processed": last_processed,
        "start_number": start_number,
        "end_number": end_number
    }
    with open(progress_file, 'w') as f:
        json.dump(progress_data, f)

# Function to fetch URLs in the specified range and save them to a JSON file
def fetch_urls(base_url, start_number, end_number, progress_file, json_file):
    """Fetch URLs in the specified range and save them to a JSON file."""
    for i in tqdm(range(start_number, end_number + 1), desc="Fetching URLs"):
        url = f"{base_url}{i:05}"
        title, extension = get_title(url)

        if title:
            file_data = {
                "FILE NAME": clean_file_name(title),
                "URL": url,
                "EXTENSION": extension
            }
            print(f"URL: {url} saved.")  # Display the link
            append_to_json(json_file, file_data)  # Append data to JSON

            # Update the progress after each successful fetch
            update_progress(progress_file, i, start_number, end_number)

    print(f"\nProcess complete. JSON saved to {json_file}.")
    
    # Properly close the JSON array
    with open(json_file, "a") as f:
        f.write("\n]")

# Main function to handle user interaction and control flow
def main():
    base_url = "https://hblinks.pro/archives/"
    progress_file = "temp_progress.json"
    json_directory = "./json"

    # Ensure the JSON directory exists
    os.makedirs(json_directory, exist_ok=True)

    # Initialize start and end numbers
    start_number = None
    end_number = None

    # Check if progress file exists
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            try:
                progress_data = json.load(f)
                last_processed = progress_data.get("last_processed")
                start_number = progress_data.get("start_number")
                end_number = progress_data.get("end_number")

                if last_processed:
                    print(f"Existing progress found. Last processed: {last_processed}")
                    continue_task = input("Do you want to continue from the last progress? (y/n): ").strip().lower()

                    if continue_task == "y":
                        start_number = last_processed + 1  # Start from the next number
                    else:
                        start_number = int(input("Enter the starting number: "))
                        end_number = int(input("Enter the ending number: "))
                else:
                    print("Progress file is empty. Starting a new task.")
                    start_number = int(input("Enter the starting number: "))
                    end_number = int(input("Enter the ending number: "))
            except (json.JSONDecodeError, IndexError):
                print("Progress file is corrupted or empty. Starting a new task.")
                start_number = int(input("Enter the starting number: "))
                end_number = int(input("Enter the ending number: "))
    else:
        start_number = int(input("Enter the starting number: "))
        end_number = int(input("Enter the ending number: "))

    # Create a JSON file to store the results
    json_file = os.path.join(json_directory, f"{start_number}-{end_number}.json")

    # Fetch URLs and save to JSON
    try:
        fetch_urls(base_url, start_number, end_number, progress_file, json_file)
    except KeyboardInterrupt:
        print("Process stopped by user.")
        # Update progress before exit
        update_progress(progress_file, start_number - 1, start_number, end_number)

if __name__ == "__main__":
    main()