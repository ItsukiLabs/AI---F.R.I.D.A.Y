"""M5 Device Abstraction Layer.

Sprint 3 starts with a mock home only (``mock_home.py``): no hardware, no
Home Assistant, just device state in memory. It exists to (1) exercise the
M4 catalog with a real provider that ``sync()``s its tools, and (2) make the
M2 v2 A2 question concrete: what counts as "officially happened" when a
turn changes a device and then fails.
"""

from backend.devices.mock_home import (
    MOCK_HOME_DOMAIN,
    MOCK_HOME_PROVIDER,
    DeviceError,
    FailureMode,
    MockDevice,
    MockHome,
    MockHomeAdapter,
    default_home,
)

__all__ = [
    "MOCK_HOME_DOMAIN",
    "MOCK_HOME_PROVIDER",
    "DeviceError",
    "FailureMode",
    "MockDevice",
    "MockHome",
    "MockHomeAdapter",
    "default_home",
]
