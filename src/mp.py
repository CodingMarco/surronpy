import gc
import asyncio
import bms_params
import global_data
from micropython_serial import MicropythonSerial
from surron_bms_communication import SurronBmsCommunication
from surron_communication import SurronCommunication
from bms_requestor import BmsRequestor
from esc_responder import EscResponder


def print_params_dict(params: dict):
    s = ""
    for param_id, value in params.items():
        s += f"{param_id.name}: {bms_params.decode_bms_data(param_id, value)}, "

    print(s)


async def print_params():
    while True:
        await asyncio.sleep_ms(100)
        if global_data.bms_params_slow_updated:
            print("BMS slow updated: ", end="")
            print_params_dict(global_data.bms_params_slow)
            global_data.bms_params_slow_updated = False
        if global_data.bms_params_fast_updated:
            print("BMS fast updated: ", end="")
            print_params_dict(global_data.bms_params_fast)
            global_data.bms_params_fast_updated = False
        if global_data.esc_params_updated:
            print("ESC updated: ", global_data.esc_params)
            global_data.esc_params_updated = False
        gc.collect()


async def main():
    ser_bms = MicropythonSerial(tx_pin=39, rx_pin=35, tx_enable_pin=37)
    ser_esc = MicropythonSerial(tx_pin=3, rx_pin=11, tx_enable_pin=12)
    bms_comm = SurronBmsCommunication(SurronCommunication(serial=ser_bms))
    esc_comm = SurronCommunication(serial=ser_esc)

    params_slow = [
        # Read by ESC
        bms_params.Unknown_7,
        bms_params.Temperatures,
        bms_params.BatteryPercent,
        bms_params.BmsStatus,
        # Other stuff
        bms_params.TotalCapacity,
        bms_params.ChargeCycles,
        bms_params.History,
        bms_params.CellVoltages1,
    ]

    params_fast = [
        # Read by ESC
        bms_params.BatteryVoltage,
        # Other stuff
        bms_params.BatteryCurrent,
        bms_params.RemainingCapacity,
        bms_params.Statistics,
    ]

    bms_requestor = BmsRequestor(bms_comm, params_slow, params_fast)
    esc_responder = EscResponder(esc_comm)

    tasks = [
        # bms_requestor.run(),
        esc_responder.run(),
        print_params(),
    ]

    await asyncio.gather(*tasks)


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        asyncio.new_event_loop()
        print("run() to run again.")
