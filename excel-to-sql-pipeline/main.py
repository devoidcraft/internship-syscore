import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

from utils import load_json, ensure_folder
from excel_reader import read_excel
from sql_generator import generate_create_table, generate_insert
from logger import setup_logger

logger = setup_logger()

SCHEMA = load_json("config/schema.json")
MAPPING = load_json("config/mapping.json")

INPUT_FOLDER = "input_excels"
OUTPUT_FOLDER = "output_sql"

ensure_folder(OUTPUT_FOLDER)

OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "final_output.sql")


def process_file(file_name):
    try:
        if not file_name.endswith(".xlsx"):
            return ""

        file_path = os.path.join(INPUT_FOLDER, file_name)

        df = read_excel(file_path)
        if df is None or df.empty:
            logger.warning(f"Empty file: {file_name}")
            return ""

        table_key = MAPPING.get("file_to_table", {}).get(file_name)
        if not table_key:
            logger.warning(f"No mapping for: {file_name}")
            return ""

        schema = SCHEMA.get(table_key)
        if not schema:
            logger.warning(f"No schema for: {table_key}")
            return ""

        create_sql = generate_create_table(schema)
        insert_sql = generate_insert(df, schema)

        logger.info(f"Processed: {file_name}")

        return f"{create_sql}\n{insert_sql}\n\n"

    except Exception as e:
        logger.error(f"Failed: {file_name} | {e}")
        return ""


def main():
    files = os.listdir(INPUT_FOLDER)
    results = []

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, f) for f in files]

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing"
        ):
            result = future.result()
            if result:
                results.append(result)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(results)

    logger.info("All files processed!")


if __name__ == "__main__":
    main()
