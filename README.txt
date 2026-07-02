Prerequisites
pip install pandas openpyxl




```text
├── input_excels/        # Place your raw .xlsx files here
├── output_json/         # Individual .json files are generated here
├── output_combined/     # Contains the single combined_reviews.json
├── output_zip/          # Contains the packaged all_results.zip
├── config/
│   └── mapping.json     # Configuration for target review phases
├── utils/
│   ├── excel_parser.py  # Core logic for reading and cleaning the Excel data
│   └── comment_extractor.py # Regex/parsing logic for isolating specific comments
└── main.py              # The main orchestrator script




The Configuration (mapping.json):
Think of this as the remote control. We use it to tell the program exactly which review phase we care about (e.g., perf-pre). It maps that phase to the exact heading we need to look for in the Excel file.

The Extractor (comment_extractor.py):
This is the precision tool. It looks inside the giant block of text in the review comment cell, finds our specific target heading, and extracts only the text directly underneath it, stopping exactly when the next phase begins.

The Cleaner (excel_parser.py):
This script handles the messy Excel structure. It opens the specific "Review Comments" sheet, scans the first 20 rows to dynamically find where the real headers start, and cleans up the Part IDs. It then pairs the cleaned part names with their points, status, and extracted comments.

The Orchestrator (main.py):
This is the manager of the assembly line. It looks in our input_excels folder, grabs every .xlsx file, and sends it through the cleaner and extractor.