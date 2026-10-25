"""M5 Device Abstraction Layer.

Sprint 3 starts with a mock home only (``mock_home.py``): no hardware, no
Home Assistant, just device state in memory. It exists to (1) exercise the
M4 catalog with a real provider that ``sync()``s its tools, and (2) make the
M2 v2 A2 question concrete: what counts as "officially happened" when a
turn changes a device and then fails.

Layers (stage 2, 2026-10-25), so a real adapter only writes the first one:

- ``DeviceDriver`` (protocol): describe devices, read state, apply changes —
  ``MockHome`` now, Home Assistant / MQTT later;
- ``DeviceService`` (``service.py``): validation, desired/reported shadow,
  operation ids, read-back with tolerance — the same for every driver;
- ``build_device_tools`` (``tools.py``): catalog tools generated from the
  devices' capabilities (contract in ``backend/schemas/device_contract.py``).
"""

from backend.devices.mock_home import (
    MOCK_HOME_DOMAIN,
    MOCK_HOME_PROVIDER,
    FailureMode,
    MockDevice,
    MockHome,
    MockHomeAdapter,
    default_home,
    two_lamp_home,
)
from backend.devices.service import CommandAccepted, DeviceDriver, DeviceError, DeviceService
from backend.devices.tools import build_device_tools

__all__ = [
    "MOCK_HOME_DOMAIN",
    "MOCK_HOME_PROVIDER",
    "CommandAccepted",
    "DeviceDriver",
    "DeviceError",
    "DeviceService",
    "FailureMode",
    "MockDevice",
    "MockHome",
    "MockHomeAdapter",
    "build_device_tools",
    "default_home",
    "two_lamp_home",
]
