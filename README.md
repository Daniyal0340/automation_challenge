# LA Times Article Bot

## Overview
The LA Times Article Bot is a Python script designed to automate the process of searching for articles on the Los Angeles Times website, sorting them by newest, extracting relevant information such as news title, description, date, and amount (if present), and saving this data into an Excel spreadsheet.

## Prerequisites
- Python 3.x installed on your system
- Python libraries: requests, rpaframework

## Installation
1. Clone or download the repository to your local machine.
2. Install the required Python libraries using pip:
   ```bash
   pip install requests
   pip install rpaframework
   ```

## Usage
1. Run the `task.py` script.
2. The bot will prompt you to enter the search query for the articles you want to retrieve.
3. The bot will then scrape the LA Times website, search for articles matching the query, sort them by newest, and extract title, description, date & amount (if present).
4. Finally, the bot will save the extracted data into an Excel spreadsheet named `la_times.xlsx`.

## Configuration
- You can modify the script to change the search query or adjust the extraction process as needed.
- Ensure that you have a stable internet connection to retrieve the latest articles from the LA Times website.

## Sample Output
The Excel spreadsheet generated by the bot will contain columns for:
- News Title
- Description
- Date
- Amount (if present)

## Notes
- This script relies on web scraping techniques and may be affected by changes to the structure of the LA Times website.
- Use responsibly and ensure compliance with the LA Times website's terms of service.

## License
This project is licensed under the [MIT License](LICENSE).