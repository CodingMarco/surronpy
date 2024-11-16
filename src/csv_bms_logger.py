from surron_bms_communication import SurronBmsCommunication
from surron_communication import SurronCommunication
from serial_communication import SerialCommunication
import csv
import time
import bms_params
import logging
from datetime import datetime


running_params_scalar = [
    bms_params.RtcTime,
    bms_params.BatteryVoltage,
    bms_params.BatteryCurrent,
    bms_params.BatteryPercent,
    bms_params.BatteryHealth,
    bms_params.RemainingCapacity,
    bms_params.TotalCapacity,
    bms_params.ChargeCycles,
]


def main():
    comm = SurronCommunication(serial=SerialCommunication("/dev/ttyUSB0"))
    bms_comm = SurronBmsCommunication(comm)

    logging.basicConfig(level=logging.DEBUG)

    csv_file = open("bms_data.csv", "w")
    writer = csv.writer(csv_file)

    title_line = [param.name for param in running_params_scalar]
    title_line += [f"CellTemperature{i}" for i in range(1, 4)]
    title_line += [
        "DischargeFetTemperature",
        "ChargeFetTemperature",
        "SoftStartCircuitTemperature",
        "LifetimeCharged",
        "CurrentCycleCharged",
    ]
    title_line += [f"Cell{i}Voltage" for i in range(1, 17)]

    writer.writerow(title_line)

    while True:
        data_line = []
        for param in running_params_scalar:
            param_value = bms_comm.read_parameter(param)
            if type(param_value) is datetime:
                data_line.append(param_value.isoformat())
            else:
                data_line.append(param_value)

        temperatures = bms_comm.read_parameter(bms_params.Temperatures)
        for temp in temperatures["cell_temperatures"]:
            data_line.append(temp)

        data_line.append(temperatures["discharge_fet"])
        data_line.append(temperatures["charge_fet"])
        data_line.append(temperatures["soft_start_circuit"])

        statistics = bms_comm.read_parameter(bms_params.Statistics)
        data_line.append(statistics["lifetime_charged"])
        data_line.append(statistics["current_cycle"])

        data_line += bms_comm.read_parameter(bms_params.CellVoltages1)

        writer.writerow(data_line)
        csv_file.flush()

        time.sleep(1)


if __name__ == "__main__":
    main()
