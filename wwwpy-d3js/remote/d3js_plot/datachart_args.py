from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union

from pydantic import BaseModel

from .api_base import ApiBase
from .uds_name_entry import UdsNameEntry

from enum import Enum

class DisplayMode(str, Enum):
    Band = "band"
    Mask = "mask"
    Line = "line"
    Label = "label"
    Hidden = "hidden"


class Column(ApiBase):
    name: str
    display_mode: DisplayMode
    values_color: Dict[str, str] = dict()
    circle_size: Optional[float]
    color: Optional[str]
    labels: Optional[List[str]]


ValuesType = List[
    Union[
        Optional[float],
        Optional[datetime],
        Optional[str]
    ]
]


class ValueColumn(Column):
    values: ValuesType


class ApiPydanticTestRequest(ApiBase):
    window: Tuple[datetime, datetime]


class ApiPydanticTestResponse(ApiBase):
    values: List[float]


class ApiDatachartCsvListResponse(ApiBase):
    entries: List[UdsNameEntry]



class ApiDatachartCsvInfoRequest(ApiBase):
    csv_file: str  # could be renamed to `datasource_name`


class ApiDatachartCsvInfoResponse(ApiBase):
    timestamp_min_max: Tuple[datetime, datetime]
    columns: List[Column]


class ApiDatachartCsvDataRequest(ApiDatachartCsvInfoRequest):
    timestamp_min_max: Tuple[datetime, datetime]
    columns_name: List[str]


class ColumnValues(ApiBase):
    name: str
    values: ValuesType


class ApiDatachartCsvDataResponse(ApiBase):
    timestamp_values: List[datetime]
    column_values: List[ColumnValues]
