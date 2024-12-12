import subprocess
import sys
import time
import csv
import argparse
from datetime import datetime

def measure_cpu_usage(duration=15, output_file="cpu_usage.log"):
    """Measure CPU usage for a specified duration and save the results to a file."""
    try:
        print(f"Measuring CPU usage for {duration} seconds...")

        # Run the mpstat command with LANG=C to ensure consistent formatting
        with open(output_file, "w") as file:
            process = subprocess.Popen(
                ["timeout", str(duration), "mpstat", "-P", "ALL", "1"],
                stdout=file,
                stderr=subprocess.PIPE,
                text=True,
                env={"LANG": "C"},  # Set LANG=C explicitly
            )
            _, stderr = process.communicate()

            if process.returncode not in (0, 124):  # 124 is timeout's exit code for a successful timeout
                print(f"Error while executing mpstat: {stderr.strip()}")
                sys.exit(1)

        # Remove unnecessary header and extra lines
        with open(output_file, 'r') as infile:
            lines = infile.readlines()

        # Skip the first 2 lines (header)
        with open(output_file, 'w') as outfile:
            outfile.writelines(lines[2:])
        
        print(f"Results saved to {output_file}")

    except FileNotFoundError:
        print("Error: 'mpstat' or 'timeout' command not found. Please install sysstat and coreutils.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def convert_to_csv(input_file, output_file):
    """Convert the CPU usage log file to CSV format."""
    try:
        header = ['time', 'CPU', '%usr', '%nice', '%sys', '%iowait', '%irq', '%soft', '%steal', '%guest', '%gnice', '%idle']
        data = []

        # Read the input log file
        with open(input_file, 'r') as infile:
            lines = infile.readlines()

        # Process each line and store CPU usage data
        current_time = None
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and header lines
            if not line or line.startswith('CPU'):
                continue
            
            # Extract timestamp and CPU usage data
            if line[0].isdigit():
                parts = line.split()
                time = parts[0]
                if current_time != time:
                    current_time = time
                
                cpu_stats = [current_time] + parts[1:]
                data.append(cpu_stats)

        # Write the CSV output
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)  # Write the header
            writer.writerows(data)  # Write the data rows
        
        print(f"CSV file created: {output_file}")

    except Exception as e:
        print(f"Error converting to CSV: {e}")
        sys.exit(1)

def remove_cpu_rows(input_file, output_file):
    """Remove rows where the second column is 'CPU' except when the first column is 'time'."""
    try:
        with open(input_file, 'r') as infile:
            reader = csv.reader(infile)
            lines = list(reader)

        filtered_lines = []

        # Process each line
        for line in lines:
            if len(line) > 1 and line[1].strip() == "CPU" and line[0].strip() != "time":
                continue
            filtered_lines.append(line)

        # Write the filtered lines to the output file
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(filtered_lines)

        print(f"Filtered data saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def sort_cpu_data(input_csv, output_csv):
    """Sort CPU data with 'all' CPU rows first, then other rows in ascending order."""
    try:
        with open(input_csv, mode='r', newline='') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)

        all_row = [row for row in rows if row['CPU'] == 'all']
        other_rows = [row for row in rows if row['CPU'] != 'all']
        sorted_rows = all_row + sorted(other_rows, key=lambda x: int(x['CPU']))

        # Write sorted rows to the output file
        with open(output_csv, mode='w', newline='') as outfile:
            fieldnames = sorted_rows[0].keys()  # Get header from the first row
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_rows)

        print(f"Sorted data saved to {output_csv}")
    
    except Exception as e:
        print(f"Error sorting data: {e}")
        sys.exit(1)

def process_file(input_file, output_file):
    """Process file to group CPU data by time and compute time differences."""
    try:
        with open(input_file, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader)
            header[0] = 'time'  # Rename the first column
            data = list(reader)
        
        grouped_data = {}
        for row in data:
            cpu = row[1]
            time_str = row[0]
            time_obj = datetime.strptime(time_str, '%H:%M:%S')

            if cpu not in grouped_data:
                grouped_data[cpu] = {'start_time': time_obj, 'rows': []}
            
            time_diff = (time_obj - grouped_data[cpu]['start_time']).total_seconds()
            row[0] = str(int(time_diff))
            grouped_data[cpu]['rows'].append(row)

        # Write processed data to the output file
        with open(output_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            for cpu in grouped_data:
                for row in grouped_data[cpu]['rows']:
                    writer.writerow(row)

        print(f"Processed data saved to {output_file}")

    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure CPU usage and save to a file, then convert to CSV.")
    parser.add_argument("duration", type=int, nargs="?", default=15, help="Duration to measure CPU usage in seconds (default: 15)")
   # parser.add_argument("output_file", type=str, nargs="?", default="cpu_usage.log", help="Output log file to save results (default: cpu_usage.log)")
    parser.add_argument("csv_file", type=str, nargs="?", default="cpu_usage.csv", help="Output CSV file (default: cpu_usage.csv)")
    outputfile = "cpu_usage.log"
    args = parser.parse_args()

    # Measure CPU usage and save to log file
    measure_cpu_usage(args.duration,  outputfile)

    # Convert the log file to CSV format
    convert_to_csv( outputfile, args.csv_file)
    remove_cpu_rows(args.csv_file, args.csv_file)
    sort_cpu_data(args.csv_file, args.csv_file)
    process_file(args.csv_file, args.csv_file)
