import pandas as pd


def read_excel(file_path):
    try:
        df = pd.read_excel(file_path)

        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        df.fillna("", inplace=True)

        return df

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
