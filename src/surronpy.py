from surron_communication import SurronCommunication
from serial_communication import SerialCommunication
import bms_params
from bms_params import BmsParameterId
import logging


def main():
    comm = SurronCommunication(serial=SerialCommunication("/dev/ttyUSB0"))

    logging.basicConfig(level=logging.DEBUG)

    for param in BmsParameterId:
        data = comm.read_bms_parameter(param)
        decoded = bms_params.decode_bms_data(param, data)
        if type(decoded) is not bytes:
            print(f"{param.name}: {decoded}")


if __name__ == "__main__":
    main()
