#!/usr/bin/python

import RPi.GPIO as GPIO
import time


def write_table_mode_1(line_num, table_mode):
    with open("table_mode.txt", "w") as file:
        file.write(table_mode)

def read_table_mode_1():
    with open("table_mode.txt", "r") as file:
        content = file.read()
        return content

def write_table_mode(line_number, new_data):

    file_path = "table_mode.txt"

    with open(file_path, 'r') as file:
        lines = file.readlines()

    lines[line_number - 1] = new_data + '\n'

    with open(file_path, 'w') as file:
        file.writelines(lines)

def read_table_mode(line_number):
    
    file_path = "table_mode.txt"
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    return lines[line_number - 1].strip()


if __name__ == "__main__":

    try:
        table_mode_1 = "initial"
        table_mode_2 = "btn_off"
        write_table_mode(1, table_mode_1)
        write_table_mode(2, table_mode_2)
        print("File created and written.")

        content1 = read_table_mode(1)
        print("File Content 1:")
        print(content1)
        content2 = read_table_mode(2)
        print("File Content 2:")
        print(content2)
    
    except KeyboardInterrupt:
        print("Exiting program...")
    
    finally:
        print("All cleanup complete.")
