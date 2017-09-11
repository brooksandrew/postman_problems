import csv
from io import StringIO


def create_mock_csv_from_dataframe(df):
    """
    Converts a pandas DataFrame to a StringIO object.
    Used to mock tests of functions that read from the filesystem, so we only need to keep track of one source of truth.

    Args:
        df (pandas dataframe): to be converted into a StringIO object

    Returns: io.StringIO representation of `df`
    """

    csvfile = StringIO()
    csvfile.seek(0)
    fieldnames = df.columns
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in df.iterrows():
        writer.writerow(row[1].to_dict())
    csvfile.seek(0)

    return csvfile