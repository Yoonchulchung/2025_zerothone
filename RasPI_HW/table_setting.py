#!/usr/bin/python

import time
import os
from table_mode import write_table_mode


# file_name
file_name_open = "./servo_move/servo_open.py"
file_name_up = "./servo_move/servo_up.py"


if __name__ == "__main__":

    try:
        print("Table is setting")
        exit_code = os.system(file_name_open)
        time.sleep(0.5)
        exit_code = os.system(file_name_up)
        time.sleep(0.5)
        write_table_mode(1, "setting")
        print(f"Exit code: {exit_code}")
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        print("cleanup complete.")
