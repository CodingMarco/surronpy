import asyncio
import bms_params
from micropython_serial import MicropythonSerial
from surron_bms_communication import SurronBmsCommunication
from surron_communication import SurronCommunication


running_params_scalar = [
    bms_params.RtcTime,
    bms_params.BatteryVoltage,
    bms_params.BatteryCurrent,
    bms_params.BatteryPercent,
    bms_params.RemainingCapacity,
    bms_params.TotalCapacity,
    bms_params.ChargeCycles,
]


async def main():
    ser = MicropythonSerial(tx_pin=39, rx_pin=35, tx_enable_pin=37)
    comm = SurronCommunication(serial=ser)
    bms_comm = SurronBmsCommunication(comm)

    while True:
        for param in running_params_scalar:
            param_value = await bms_comm.read_parameter(param)
            print(param.name, param_value)


def run_main():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        asyncio.new_event_loop()
        print("run_main() to run again.")
