import struct
from enum import Enum
from typing import Union
from datetime import datetime, date

BMS_ADDRESS = 0x116


class BmsParameterId(Enum):
    Unknown_0 = 0
    Unknown_7 = 7
    Temperatures = 8
    BatteryVoltage = 9
    BatteryCurrent = 10
    BatteryPercent = 13
    BatteryHealth = 14
    RemainingCapacity = 15
    TotalCapacity = 16
    Unknown_17 = 17
    Unknown_20 = 20
    Statistics = 21
    BmsStatus = 22
    ChargeCycles = 23
    DesignedCapacity = 24
    DesignedVoltage = 25
    Versions = 26
    ManufacturingDate = 27
    Unknown_28 = 28
    RtcTime = 29
    Unknown_30 = 30
    BmsManufacturer = 32
    BatteryModel = 33
    CellType = 34
    SerialNumber = 35
    CellVoltages1 = 36
    CellVoltages2 = 37
    History = 38
    Unknown_39 = 39
    Unknown_48 = 48
    Unknown_120 = 120
    Unknown_160 = 160

    @property
    def length(self) -> int:
        return BmsParameterId.get_length(self)

    @staticmethod
    def get_length(parameter_id: "BmsParameterId") -> int:
        lengths = {
            BmsParameterId.Unknown_0: 4,
            BmsParameterId.Unknown_7: 1,
            BmsParameterId.Temperatures: 8,
            BmsParameterId.BatteryVoltage: 4,
            BmsParameterId.BatteryCurrent: 4,
            BmsParameterId.BatteryPercent: 1,
            BmsParameterId.BatteryHealth: 4,
            BmsParameterId.RemainingCapacity: 4,
            BmsParameterId.TotalCapacity: 4,
            BmsParameterId.Unknown_17: 2,
            BmsParameterId.Unknown_20: 4,
            BmsParameterId.Statistics: 12,
            BmsParameterId.BmsStatus: 10,
            BmsParameterId.ChargeCycles: 4,
            BmsParameterId.DesignedCapacity: 4,
            BmsParameterId.DesignedVoltage: 4,
            BmsParameterId.Versions: 8,
            BmsParameterId.ManufacturingDate: 3,
            BmsParameterId.Unknown_28: 4,
            BmsParameterId.RtcTime: 6,
            BmsParameterId.Unknown_30: 6,
            BmsParameterId.BmsManufacturer: 16,
            BmsParameterId.BatteryModel: 32,
            BmsParameterId.CellType: 16,
            BmsParameterId.SerialNumber: 32,
            BmsParameterId.CellVoltages1: 32,
            BmsParameterId.CellVoltages2: 32,
            BmsParameterId.History: 14,
            BmsParameterId.Unknown_39: 64,
            BmsParameterId.Unknown_48: 64,
            BmsParameterId.Unknown_120: 64,
            BmsParameterId.Unknown_160: 32,
        }

        if parameter_id in lengths:
            return lengths[parameter_id]
        else:
            raise ValueError(f"Unknown parameter {parameter_id}")


def decode_bms_data(
    parameter_id: BmsParameterId, data: bytes
) -> Union[
    float, int, list[float], dict[str, Union[float, int]], str, datetime, date, bytes
]:
    if parameter_id == BmsParameterId.Temperatures:
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
    elif parameter_id == BmsParameterId.BatteryVoltage:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == BmsParameterId.BatteryCurrent:
        return struct.unpack("<i", data)[0] / 1000.0
    elif parameter_id == BmsParameterId.BatteryPercent:
        return data[0]
    elif parameter_id == BmsParameterId.BatteryHealth:
        return data[0]
    elif parameter_id == BmsParameterId.RemainingCapacity:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == BmsParameterId.TotalCapacity:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == BmsParameterId.Statistics:
        total_capacity = struct.unpack("<I", data[0:4])[0] / 1000.0
        lifetime_charged = struct.unpack("<I", data[4:8])[0] / 1000.0
        current_cycle = struct.unpack("<I", data[8:12])[0] / 1000.0
        return {
            "total_capacity": total_capacity,
            "lifetime_charged": lifetime_charged,
            "current_cycle": current_cycle,
        }
    elif parameter_id == BmsParameterId.ChargeCycles:
        return struct.unpack("<I", data)[0]
    elif parameter_id == BmsParameterId.DesignedCapacity:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == BmsParameterId.DesignedVoltage:
        return struct.unpack("<I", data)[0] / 1000.0
    elif parameter_id == BmsParameterId.Versions:
        sw_version = f"{data[1]}.{data[0]}"
        hw_version = f"{data[3]}.{data[2]}"
        idx = data[4:8].decode("ascii").strip()
        return {"sw_version": sw_version, "hw_version": hw_version, "idx": idx}
    elif parameter_id == BmsParameterId.ManufacturingDate:
        return date(2000 + data[0], data[1], data[2])
    elif parameter_id == BmsParameterId.RtcTime:
        return datetime(2000 + data[0], data[1], data[2], data[3], data[4], data[5])
    elif parameter_id in {
        BmsParameterId.BmsManufacturer,
        BmsParameterId.BatteryModel,
        BmsParameterId.CellType,
        BmsParameterId.SerialNumber,
    }:
        return data.decode("ascii").strip()
    elif parameter_id in {BmsParameterId.CellVoltages1, BmsParameterId.CellVoltages2}:
        voltages = [
            struct.unpack("<H", data[i : i + 2])[0] / 1000.0 for i in range(0, 32, 2)
        ]
        return voltages
    elif parameter_id == BmsParameterId.History:
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
        BmsParameterId.BatteryVoltage,
        BmsParameterId.BatteryCurrent,
        BmsParameterId.BatteryPercent,
        BmsParameterId.BatteryHealth,
        BmsParameterId.RemainingCapacity,
        BmsParameterId.TotalCapacity,
        BmsParameterId.ChargeCycles,
        BmsParameterId.DesignedCapacity,
        BmsParameterId.DesignedVoltage,
        BmsParameterId.ManufacturingDate,
        BmsParameterId.RtcTime,
        BmsParameterId.BmsManufacturer,
        BmsParameterId.BatteryModel,
        BmsParameterId.CellType,
        BmsParameterId.SerialNumber,
    ]
