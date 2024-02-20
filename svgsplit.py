#!/usr/bin/env python3

import os
import re

def main():
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: {} input_file.svg".format(sys.argv[0]))
        sys.exit(1)

    input_file = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_directory = "{}_output".format(base_name)
    os.makedirs(output_directory, exist_ok=True)

    max_size_kb = 14
    current_file_size = 0
    file_counter = 1
    current_output_file = "{}/{}_{}.svg".format(output_directory, base_name, file_counter)
    line_count = 0

    # Extract width and height values from the input file
    with open(input_file, 'r') as f:
        content = f.read()
        width_match = re.search(r'width="([^"]*)"', content)
        height_match = re.search(r'height="([^"]*)"', content)
        width = width_match.group(1) if width_match else ''
        height = height_match.group(1) if height_match else ''

    with open(input_file, 'r') as f:
        for line in f:
            # Calculate the size of the current line
            line_size = len(line)
            # Check if adding the current line would exceed the maximum size
            if current_file_size + line_size > max_size_kb * 1024:
                # Start a new output file
                current_file_size = 0
                line_count = 0
                file_counter += 1
                current_output_file = "{}/{}_{}.svg".format(output_directory, base_name, file_counter)
                with open(current_output_file, 'w') as output_f:
                    output_f.write('<?xml version="1.0" standalone="yes"?>\n')
                    output_f.write('<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}">\n'.format(width, height))

            # Append the line to the current output file
            with open(current_output_file, 'a') as output_f:
                output_f.write(line)

            # Update the current file size and line count
            current_file_size += line_size
            line_count += 1

    # Check if the last line of each file is not </svg> and append it if necessary
    for i in range(1, file_counter + 1):
        current_output_file = "{}/{}_{}.svg".format(output_directory, base_name, i)
        with open(current_output_file, 'a') as output_f:
            if not output_f.read().endswith('</svg>\n'):
                output_f.write('</svg>\n')

    print("Splitting complete. Files created in {}: {}_1.svg, {}_2.svg, ...".format(output_directory, base_name, base_name))

if __name__ == "__main__":
    import sys
    main()
