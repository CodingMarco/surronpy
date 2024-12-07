import gc
import asyncio
import bms_params
from micropython_serial import MicropythonSerial
from surron_bms_communication import SurronBmsCommunication
from surron_communication import SurronCommunication


params_scalar = [
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
    # gc.threshold(1000)

    i = 0
    while True:
        try:
            values = [str(gc.mem_free())]
            for param in params_scalar:
                param_value = await bms_comm.read_parameter(param)
                values.append(f"{param.name}: {param_value}")
            print(", ".join(values))
            i += 1
        except Exception as e:
            print(e)


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        asyncio.new_event_loop()
        print("run_main() to run again.")
