"""rer
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from functools import cached_property
from json import dumps
from typing import TYPE_CHECKING

from .utils import get_status_code_string

