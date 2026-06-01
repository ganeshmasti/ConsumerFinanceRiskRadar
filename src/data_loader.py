import pandas as pd

from src.constants import REQUIRED_COLUMNS

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
ALLOWED_UPLOAD_EXTENSIONS = {".csv", ".tsv"}


def _read_csv_flexible(source) -> pd.DataFrame:
    """Read CSV or TSV input flexibly and handle common delimiter/tokenization issues."""
    _rewind_if_possible(source)
    try:
        return pd.read_csv(source, sep=None, engine="python").rename(columns=lambda col: str(col).strip())
    except pd.errors.ParserError:
        _rewind_if_possible(source)
        try:
            return pd.read_csv(source, sep="\t", engine="python").rename(columns=lambda col: str(col).strip())
        except pd.errors.ParserError:
            _rewind_if_possible(source)
            return pd.read_csv(source, sep=",", engine="python").rename(columns=lambda col: str(col).strip())


def load_sample_data(data_path: str) -> pd.DataFrame:
    """Load the sample complaint CSV and validate the required columns."""
    df = _read_csv_flexible(data_path)
    _validate_required_columns(df)
    df, _ = _prepare_dataframe(df)
    return df


def _rewind_if_possible(source) -> None:
    if hasattr(source, "seek"):
        source.seek(0)


def _validate_uploaded_file(file_uploader) -> None:
    name = getattr(file_uploader, "name", "uploaded.csv")
    extension = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError("Uploaded file must be a CSV or TSV file.")

    size = getattr(file_uploader, "size", None)
    if size is None and hasattr(file_uploader, "getbuffer"):
        size = len(file_uploader.getbuffer())
    if size is not None and size > MAX_UPLOAD_BYTES:
        raise ValueError("Uploaded file is too large. Please use a CSV under 20 MB.")


def _validate_required_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df.empty:
        raise ValueError("The uploaded dataset has the required columns but no complaint rows.")


def _validate_data_quality(df: pd.DataFrame) -> list[str]:
    warnings = []
    if "Date received" in df.columns and df["Date received"].isna().any():
        warnings.append("Some records have missing or invalid 'Date received' values.")
    if "State" in df.columns and df["State"].isna().any():
        warnings.append("Some records are missing a state value.")
    if "Company" in df.columns and df["Company"].isna().any():
        warnings.append("Some records are missing a company name.")
    if "Consumer disputed?" in df.columns:
        normalized = df["Consumer disputed?"].astype(str).str.strip().str.title()
        if not normalized.isin(["Yes", "No"]).all():
            warnings.append("'Consumer disputed?' contains values other than Yes/No.")
    return warnings


def _prepare_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    warnings = []
    if "Date received" in df.columns:
        parsed_dates = pd.to_datetime(df["Date received"], errors="coerce", format="mixed")
        invalid_dates = int(parsed_dates.isna().sum())
        df = df.copy()
        df["Date received"] = parsed_dates
        if invalid_dates:
            warnings.append(
                f"Removed {invalid_dates} rows with missing or invalid 'Date received' values."
            )
            df = df.dropna(subset=["Date received"])
        if df.empty:
            raise ValueError("No valid complaint rows remain after date validation.")

    df = _neutralize_spreadsheet_formulas(df)
    return df, warnings + _validate_data_quality(df)


def _neutralize_spreadsheet_formulas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    formula_prefixes = ("=", "+", "-", "@")
    for column in df.select_dtypes(include="object").columns:
        values = df[column].astype("string")
        mask = values.str.strip().str.startswith(formula_prefixes, na=False)
        if mask.any():
            df.loc[mask, column] = values[mask].apply(lambda value: "'" + value)
    return df


def load_data(file_uploader, default_path: str) -> tuple[pd.DataFrame, list[str]]:
    """Load data from a file uploader or fallback to the default sample dataset."""
    if file_uploader is not None:
        _validate_uploaded_file(file_uploader)
        try:
            df = _read_csv_flexible(file_uploader)
        except Exception as exc:
            raise ValueError(f"Unable to read uploaded file: {exc}")

        _validate_required_columns(df)
        df, warnings = _prepare_dataframe(df)
        return df, ["Uploaded dataset loaded successfully."] + warnings

    df = load_sample_data(default_path)
    warnings = _validate_data_quality(df)
    return df, ["Loaded offline sample dataset."] + warnings
