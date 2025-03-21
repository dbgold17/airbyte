#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


class CustomExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response, **kwargs) -> List[Mapping[str, Any]]:
        data = response.json().get("data")
        extracted_records = []
        self.primary_key = "id"
        if not data:
            return extracted_records

        for element in data:
            relationships: Dict[str, List[int]] = dict()
            for r_type, relations in element.get("relationships", {}).items():
                if relations.get("data"):
                    data = relations.get("data", [])

                    if isinstance(data, dict):
                        data = [data]

                    relationships[f"{r_type}"] = [e.get("id") for e in data]

            extracted_record = {**element.get("attributes"), **{self.primary_key: element[self.primary_key], **relationships}}
            extracted_records.append(extracted_record)

        return extracted_records
