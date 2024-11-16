import struct
from transparency import date, datetime

BMS_ADDRESS = 0x116


class BmsParameterId:
    def __init__(self, name, value, length):
        self.name = name
        self.value = value
        self.length = length


Unknown_0 = BmsParameterId("Unknown_0", 0, 4)
Unknown_7 = BmsParameterId("Unknown_7", 7, 1)
Temperatures = BmsParameterId("Temperatures", 8, 8)
BatteryVoltage = BmsParameterId("BatteryVoltage", 9, 4)
BatteryCurrent = BmsParameterId("BatteryCurrent", 10, 4)
BatteryPercent = BmsParameterId("BatteryPercent", 13, 1)
BatteryHealth = BmsParameterId("BatteryHealth", 14, 4)
RemainingCapacity = BmsParameterId("RemainingCapacity", 15, 4)
TotalCapacity = BmsParameterId("TotalCapacity", 16, 4)
Unknown_17 = BmsParameterId("Unknown_17", 17, 2)
Unknown_20 = BmsParameterId("Unknown_20", 20, 4)
Statistics = BmsParameterId("Statistics", 21, 12)
BmsStatus = BmsParameterId("BmsStatus", 22, 10)
ChargeCycles = BmsParameterId("ChargeCycles", 23, 4)
DesignedCapacity = BmsParameterId("DesignedCapacity", 24, 4)
DesignedVoltage = BmsParameterId("DesignedVoltage", 25, 4)
Versions = BmsParameterId("Versions", 26, 8)
ManufacturingDate = BmsParameterId("ManufacturingDate", 27, 3)
Unknown_28 = BmsParameterId("Unknown_28", 28, 4)
RtcTime = BmsParameterId("RtcTime", 29, 6)
Unknown_30 = BmsParameterId("Unknown_30", 30, 6)
BmsManufacturer = BmsParameterId("BmsManufacturer", 32, 16)
BatteryModel = BmsParameterId("BatteryModel", 33, 32)
CellType = BmsParameterId("CellType", 34, 16)
SerialNumber = BmsParameterId("SerialNumber", 35, 32)
CellVoltages1 = BmsParameterId("CellVoltages1", 36, 32)
CellVoltages2 = BmsParameterId("CellVoltages2", 37, 32)
History = BmsParameterId("History", 38, 14)
Unknown_39 = BmsParameterId("Unknown_39", 39, 64)
Unknown_48 = BmsParameterId("Unknown_48", 48, 64)
Unknown_120 = BmsParameterId("Unknown_120", 120, 64)
Unknown_160 = BmsParameterId("Unknown_160", 160, 32)


def decode_bms_data(parameter_id: BmsParameterId, data: bytes):
    if parameter_id == Temperatures:
        temperatures = [struct.unpack("b", data[i : i + 1])[0] for i in range(3)]
        discharge_fet = struct.unpack("b", data[4:5])[0]
        charge_fet = struct.unpack("b", data[5:6])[0]
        soft_start_circuit = struct.unpack("b", data[6:7])[0]
        return {
            "cell_temperatures": temperatures,
            "discharge_fet": discharge_fet,
            "charge_fet": charge_fet,
            "soft_start_circuit": soft_start_circuit,
        }
    elif parameter_id == BatteryVoltage:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == BatteryCurrent:
        return struct.unpack("<i", data)[0] / 1000.0
    elif parameter_id == BatteryPercent:
        return data[0]
    elif parameter_id == BatteryHealth:
        return data[0]
    elif parameter_id == RemainingCapacity:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == TotalCapacity:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == Statistics:
        total_capacity = struct.unpack("<I", data[0:4])[0] / 1000.0
        lifetime_charged = struct.unpack("<I", data[4:8])[0] / 1000.0
        current_cycle = struct.unpack("<I", data[8:12])[0] / 1000.0
        return {
            "total_capacity": total_capacity,
            "lifetime_charged": lifetime_charged,
            "current_cycle": current_cycle,
        }
    elif parameter_id == ChargeCycles:
        return struct.unpack("<I", data)[0]
    elif parameter_id == DesignedCapacity:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == DesignedVoltage:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == Versions:
        sw_version = f"{data[1]}.{data[0]}"
        hw_version = f"{data[3]}.{data[2]}"
        idx = data[4:8].decode("ascii").strip()
        return {"sw_version": sw_version, "hw_version": hw_version, "idx": idx}
    elif parameter_id == ManufacturingDate:
        return date(2000 + data[0], data[1], data[2])
    elif parameter_id == RtcTime:
        return datetime(2000 + data[0], data[1], data[2], data[3], data[4], data[5])
    elif parameter_id in {
        BmsManufacturer,
        BatteryModel,
        CellType,
        SerialNumber,
    }:
        return data.decode("ascii").strip()
    elif parameter_id in {CellVoltages1, CellVoltages2}:
        voltages = [
            struct.unpack("<H", data[i : i + 2])[0] / 1000.0 for i in range(0, 32, 2)
        ]
        return voltages
    elif parameter_id == History:
        out_max = struct.unpack("<i", data[0:4])[0] / 1000.0
        in_max = struct.unpack("<i", data[4:8])[0] / 1000.0
        max_cell = struct.unpack("<H", data[8:10])[0] / 1000.0
        min_cell = struct.unpack("<H", data[10:12])[0] / 1000.0
        max_temp = struct.unpack("b", data[12:13])[0]
        min_temp = struct.unpack("b", data[13:14])[0]
        return {
            "out_max": out_max,
            "in_max": in_max,
            "max_cell_voltage": max_cell,
            "min_cell_voltage": min_cell,
            "max_temp": max_temp,
            "min_temp": min_temp,
        }
    else:
        return data


def get_scalar_params() -> list[BmsParameterId]:
    return [
        BatteryVoltage,
        BatteryCurrent,
        BatteryPercent,
        BatteryHealth,
        RemainingCapacity,
        TotalCapacity,
        ChargeCycles,
        DesignedCapacity,
        DesignedVoltage,
        ManufacturingDate,
        RtcTime,
        BmsManufacturer,
        BatteryModel,
        CellType,
        SerialNumber,
    ]
