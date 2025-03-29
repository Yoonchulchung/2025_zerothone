#!/usr/bin/python

import time
import os
from table_mode import write_table_mode


# file_name
file_name_close = "./servo_move/servo_close.py"
file_name_down = "./servo_move/servo_down.py"


if __name__ == "__main__":

    try:
        print("Table is setting")
        exit_code = os.system(file_name_down)
        time.sleep(0.5)
        exit_code = os.system(file_name_close)
        time.sleep(0.5)
        write_table_mode(1, "initial")
        print(f"Exit code: {exit_code}")
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        print("cleanup complete.")
