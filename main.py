import os
import json
import zipfile
from utils.excel_parser import process_file


def main():
    # 1. Define Paths
    input_dir = "input_excels"
    output_dir = "output_json"
    combined_dir = "output_combined"
    zip_dir = "output_zip"
    config_path = "config/mapping.json"

    # 2. Create all necessary directories
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(combined_dir, exist_ok=True)
    os.makedirs(zip_dir, exist_ok=True)

    # 3. Load config mapping
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {config_path}.")
        return

    target_phase_key = config.get("target_phase", "perf-pre")
    target_heading = config["phase_headings"].get(target_phase_key)

    if not target_heading:
        print(f"Error: Target phase '{target_phase_key}' not found in mapping.json")
        return

    all_files = os.listdir(input_dir)
    print(f"Found {len(all_files)} files in '{input_dir}'.\n")

    # Dictionary to hold the combined data from all files
    combined_data = {}
    processed_count = 0

    # 4. Process all Excel files
    for filename in all_files:
        # Looking for standard excel files (ignoring temporary hidden files)
        if filename.endswith(".xlsx") and not filename.startswith("~"):
            file_path = os.path.join(input_dir, filename)
            print(f"Processing: {filename}")

            extracted_data = process_file(file_path, target_heading)

            if extracted_data:
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{base_name}.json")

                # Save Individual JSON
                with open(output_path, "w", encoding="utf-8") as out_file:
                    json.dump(extracted_data, out_file, indent=4, ensure_ascii=False)

                # Add to combined dictionary
                combined_data[base_name] = extracted_data

                print(f"  ✅ Saved {len(extracted_data)} parts to individual JSON")
                processed_count += 1
            else:
                print(f"  ⚠️ No data extracted.")

    # 5. Generate Combined JSON & ZIP Archive if processing was successful
    if processed_count > 0:
        print("\n--- Generating Final Outputs ---")

        # Save Combined JSON
        combined_file_path = os.path.join(combined_dir, "combined_reviews.json")
        with open(combined_file_path, "w", encoding="utf-8") as combined_out:
            json.dump(combined_data, combined_out, indent=4, ensure_ascii=False)
        print(f"📁 Combined JSON saved -> {combined_file_path}")

        # Create ZIP Archive
        zip_file_path = os.path.join(zip_dir, "all_results.zip")
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add all individual JSONs to a folder inside the ZIP
            for filename in os.listdir(output_dir):
                if filename.endswith(".json"):
                    file_to_zip = os.path.join(output_dir, filename)
                    # The second argument dictates the folder structure INSIDE the zip
                    zipf.write(file_to_zip, arcname=f"individual_jsons/{filename}")

            # Add the combined JSON to the root of the ZIP
            zipf.write(combined_file_path, arcname="combined_reviews.json")

        print(f"📦 ZIP Archive created -> {zip_file_path}")

    else:
        print("\n❌ No files were successfully processed.")


if __name__ == "__main__":
    main()
