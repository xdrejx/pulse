#!/usr/bin/python3
from curses import window
import os
import struct
import subprocess
import tempfile
import time
import tkinter as tk
from turtle import color

BARS_NUMBER = 14
# OUTPUT_BIT_FORMAT = "8bit"
OUTPUT_BIT_FORMAT = "16bit"
# RAW_TARGET = "/tmp/cava.fifo"
RAW_TARGET = "/dev/stdout"

conpat = """
[general]
bars = %d
[output]
method = raw
raw_target = %s
bit_format = %s
"""

config = conpat % (BARS_NUMBER, RAW_TARGET, OUTPUT_BIT_FORMAT)
bytetype, bytesize, bytenorm = ("H", 2, 65535) if OUTPUT_BIT_FORMAT == "16bit" else ("B", 1, 255)


def run():
    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(config.encode())
        config_file.flush()

        process = subprocess.Popen(["cava", "-p", config_file.name], stdout=subprocess.PIPE)
        chunk = bytesize * BARS_NUMBER
        fmt = bytetype * BARS_NUMBER

        if RAW_TARGET != "/dev/stdout":
            if not os.path.exists(RAW_TARGET):
                os.mkfifo(RAW_TARGET)
            source = open(RAW_TARGET, "rb")
        else:
            process_stdout = process.stdout
            if process_stdout is None:
                raise ValueError("process stdout is None")
            source = process_stdout
        
        root = tk.Tk()
        canvas = tk.Canvas(root, width=100, height=100)

        last_time_printed = time.time()
        while True:
            data = source.read(chunk)
            if len(data) < chunk:
                break
            #update the saturation of the background color to be data[-1]
            color = data[-1]
            hex_color = "#{:02x}{:02x}{:02x}".format(color, color, 0)
            root.configure(background=hex_color)
            root.update()

            # sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
            sample = [i / bytenorm for i in struct.unpack(fmt, data)]
            current_time = time.time()
            if current_time - last_time_printed > 0.05:
                # visualize the values as vertical bars where 1 is the maximum height but only first half of the sample
                for i in sample[:len(sample) // 2]:
                    print("#" * int((i * 100)+ 1), end="\n")
                    print("#" * int((i * 100)+ 1), end="\n")
                    print("#" * int((i * 100)+ 1), end="\n")
                print()

                last_time_printed = current_time

if __name__ == "__main__":
    window_width = 800
    window_height = 400

    root = tk.Tk()
    root.geometry("{}x{}".format(window_width, window_height))

    color = 255
    hex_color = "#{:02x}{:02x}{:02x}".format(color, color, 0)

    root.configure(background=hex_color)

    root.mainloop()
    run()
