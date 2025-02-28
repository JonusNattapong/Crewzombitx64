import json
import csv
import logging
from typing import Dict

class DataExporter:
    @staticmethod
    async def export_to_json(data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename

    @staticmethod
    async def export_to_csv(data, filename):
        flattened_data = DataExporter._flatten_data(data)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
        return filename

    @staticmethod
    def _flatten_data(data):
        if isinstance(data, list):
            return [DataExporter._flatten_dict(item) for item in data]
        else:
            return [DataExporter._flatten_dict(data)]

    @staticmethod
    def _flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(DataExporter._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                if all(isinstance(x, dict) for x in v):
                    for i, item in enumerate(v):
                        items.extend(DataExporter._flatten_dict(item, f"{new_key}{sep}{i}", sep).items())
                else:
                    items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)
