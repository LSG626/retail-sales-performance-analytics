from pathlib import Path
import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".xlsm",
}


def read_csv_safely(file_path):
    """
    Try common encodings when reading CSV files.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "ISO-8859-1",
        "latin1",
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding
            )

        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Unable to decode CSV file: {file_path}"
    )


def load_excel_file(file_path):
    """
    Read every sheet inside an Excel workbook.
    """

    print(f"\nReading Excel workbook: {file_path.name}")

    excel_file = pd.ExcelFile(file_path)

    print(
        f"Sheets found: {excel_file.sheet_names}"
    )

    frames = []

    for sheet_name in excel_file.sheet_names:

        print(
            f"  Loading sheet: {sheet_name}"
        )

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name
        )

        # Skip completely empty sheets
        if df.empty:
            print(
                f"  Skipping empty sheet: {sheet_name}"
            )
            continue

        # Track where every row came from
        df["source_file"] = file_path.name
        df["source_sheet"] = sheet_name

        frames.append(df)

        print(
            f"  Rows loaded: {len(df):,}"
        )

    return frames


def load_csv_file(file_path):
    """
    Read one CSV file.
    """

    print(f"\nReading CSV: {file_path.name}")

    df = read_csv_safely(file_path)

    if df.empty:
        return []

    df["source_file"] = file_path.name
    df["source_sheet"] = "CSV"

    print(
        f"Rows loaded: {len(df):,}"
    )

    return [df]


def load_all_raw_data(raw_directory):
    """
    Load every supported file in data/raw.

    Excel:
        Every worksheet is loaded.

    CSV:
        Entire CSV is loaded.

    All datasets are combined together.
    """

    raw_directory = Path(raw_directory)

    if not raw_directory.exists():
        raise FileNotFoundError(
            f"Raw data folder does not exist: "
            f"{raw_directory}"
        )

    files = [
        file
        for file in raw_directory.iterdir()
        if (
            file.is_file()
            and file.suffix.lower()
            in SUPPORTED_EXTENSIONS
        )
    ]

    if not files:
        raise FileNotFoundError(
            "No supported data files found in "
            f"{raw_directory}"
        )

    print("=" * 70)
    print("RAW DATA LOADER")
    print("=" * 70)

    print(
        f"\nFiles found: {len(files)}"
    )

    all_frames = []

    for file_path in files:

        extension = file_path.suffix.lower()

        if extension == ".csv":

            frames = load_csv_file(
                file_path
            )

        elif extension in {
            ".xlsx",
            ".xls",
            ".xlsm"
        }:

            frames = load_excel_file(
                file_path
            )

        else:
            continue

        all_frames.extend(frames)

    if not all_frames:
        raise ValueError(
            "Files were found, but no usable "
            "data was loaded."
        )

    print("\nCombining datasets...")

    combined_df = pd.concat(
        all_frames,
        ignore_index=True,
        sort=False
    )

    print(
        f"Combined rows: "
        f"{len(combined_df):,}"
    )

    print(
        f"Combined columns: "
        f"{len(combined_df.columns)}"
    )

    return combined_df