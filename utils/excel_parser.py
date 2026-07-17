import pandas as pd
import re
from .comment_extractor import extract_comment


def find_header_index(file_path: str, sheet_name: str) -> int:
    df_temp = pd.read_excel(
        file_path, sheet_name=sheet_name, header=None, nrows=20, engine="openpyxl"
    )
    for idx, row in df_temp.iterrows():
        row_str = " ".join([str(val).strip() for val in row.values if pd.notnull(val)])
        if "Part" in row_str and "Status" in row_str and "Review Comment" in row_str:
            return idx
    return 0


def clean_part_name(raw_part):
    if pd.isna(raw_part) or not str(raw_part).strip():
        return None
    match = re.search(r"^([A-Z0-9\.]+)", str(raw_part).strip())
    if match and "." in match.group(1):
        return match.group(1)
    return None


def process_file(file_path: str, target_heading: str) -> list:
    sheet_name = "Review Comments"

    try:
        header_idx = find_header_index(file_path, sheet_name)
        df = pd.read_excel(
            file_path, sheet_name=sheet_name, header=header_idx, engine="openpyxl"
        )
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

    df.columns = [str(col).strip() for col in df.columns]

    required_cols = ["Part", "Status", "Review Comment"]
    for col in required_cols:
        if col not in df.columns:
            print(f"Warning: Missing column '{col}' in {file_path}")
            return []

    points_col = next((c for c in df.columns if "Point" in c), None)

    # 1. Clean up the Part IDs and replace empty ones with None
    df["Clean_Part"] = df["Part"].apply(clean_part_name)

    # 2. Fix Issue 2 & 6: Forward-fill the Clean_Part and Status down the rows.
    # This attaches the correct Part ID to the merged rows below it so data isn't lost.
    df["Clean_Part"] = df["Clean_Part"].ffill()
    df["Status"] = df["Status"].ffill()
    if points_col:
        df[points_col] = df[points_col].ffill()

    # Drop any rows that STILL don't have a valid Part ID (e.g., junk rows above the table)
    df = df.dropna(subset=["Clean_Part"])

    results = []

    # 3. Group by the Clean_Part ID to combine multi-row comments
    for part_id, group_df in df.groupby("Clean_Part", sort=False):
        # Combine all Review Comment cells for this specific part into one block of text
        raw_comments_list = [
            str(x)
            for x in group_df["Review Comment"]
            if pd.notna(x) and str(x).strip() != "nan"
        ]
        combined_comment = "\n".join(raw_comments_list)

        # Extract the specific phase comment from the newly combined block
        extracted_comment = extract_comment(combined_comment, target_heading)

        # Grab the status and points from the first row of the group
        status = str(group_df["Status"].iloc[0]).strip()
        points = str(group_df[points_col].iloc[0]).strip() if points_col else "0"
        if points == "nan":
            points = "0"

        results.append({
            "part": part_id,
            "points": points,
            "status": status,
            "review_comment": extracted_comment,
        })

    return results
