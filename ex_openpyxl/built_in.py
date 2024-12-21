import csv
from pathlib import Path


def csv_as_dict(data_file: Path) -> dict[str, str]:
    with data_file.open() as file:
        data = csv.reader(file)
        next(data)  # Row names
        return {row[0]: row[1] for row in data}


def csv_as_list(data_file: Path) -> list[dict]:
    with data_file.open() as file:
        data = csv.reader(file)
        row_names = next(data)
        return [
            {
                name: value.strip(' ').split() if name.endswith('_list') else value
                for name, value in zip(row_names, row)
            }
            for row in data
        ]


if __name__ == '__main__':
    ips = csv_as_dict(Path('nf_ips.csv'))
    print(ips)
    links = csv_as_list(Path('nf_links.csv'))
    for i in links:
        print(i)
