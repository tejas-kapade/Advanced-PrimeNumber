import os
import math
import time
import csv
from tqdm import tqdm  # Import tqdm for progress bar
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime

# Memoization cache for previously checked primes
prime_cache = {}

# Function to check if a number is prime
def is_prime(num):
    # Return cached result if available
    if num in prime_cache:
        return prime_cache[num]

    if num <= 1:
        prime_cache[num] = False
        return False
    elif num == 2:
        prime_cache[num] = True
        return True  # 2 is the only even prime number
    elif num % 2 == 0:
        prime_cache[num] = False
        return False  # All other even numbers are not prime

    # Check divisibility from 3 up to sqrt(num)
    for i in range(3, int(math.sqrt(num)) + 1, 2):  # Step by 2 to skip even numbers
        if num % i == 0:
            prime_cache[num] = False
            return False

    prime_cache[num] = True
    return True

# Function to generate all prime numbers up to a given limit
def generate_primes_up_to(n):
    primes = []
    start_time = time.time()  # Track the start time

    # Using tqdm to show a progress bar
    for i in tqdm(range(2, n + 1), desc="Generating primes", unit="number"):
        if is_prime(i):
            primes.append(i)

    return primes

# Function to generate a timestamped filename for CSV or PDF
def get_timestamped_filename(base_name, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

# Function to export primes to a CSV file
def export_to_csv(primes):
    try:
        # Ensure the 'reports' directory exists
        if not os.path.exists('reports'):
            os.makedirs('reports')

        # Generate a timestamped filename for the CSV
        filename = get_timestamped_filename("primes", ".csv")
        filepath = os.path.join('reports', filename)
        
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Prime Numbers"])
            for prime in primes:
                writer.writerow([prime])
        print(f"Prime numbers have been saved to {filepath}.")
    except Exception as e:
        print(f"Error while saving to CSV: {e}")

# Function to export primes to a PDF file in table format
def export_to_pdf(primes):
    try:
        # Ensure the 'reports' directory exists
        if not os.path.exists('reports'):
            os.makedirs('reports')

        # Generate a timestamped filename for the PDF
        filename = get_timestamped_filename("primes", ".pdf")
        filepath = os.path.join('reports', filename)

        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        
        # Prepare data for the table
        data = [["Prime Numbers"]]  # Header row
        for prime in primes:
            data.append([str(prime)])
        
        # Create the table
        table = Table(data)
        
        # Style the table
        table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Header background color
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Add gridlines
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Set font to Helvetica
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Set font size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header row
        ]))

        # Build the PDF document with the table
        doc.build([table])

        print(f"Prime numbers have been saved to {filepath}.")
    except Exception as e:
        print(f"Error while saving to PDF: {e}")

# Main function to handle user input and output
def main():
    while True:
        print("\nPrime Number Checker")
        print("1. Check if a number is prime")
        print("2. Generate all prime numbers up to a number")
        print("3. Export prime numbers to CSV")
        print("4. Export prime numbers to PDF")
        print("5. Exit")
        
        choice = input("Enter your choice (1/2/3/4/5): ")

        if choice == '1':
            try:
                num = int(input("Enter a number to check if it is prime: "))
                if num <= 1:
                    print(f"{num} is Not a Prime Number")
                elif is_prime(num):
                    print(f"{num} is a Prime Number")
                else:
                    print(f"{num} is Not a Prime Number")
            except ValueError:
                print("You entered an invalid number. Please enter an integer.")

        elif choice == '2':
            try:
                limit = int(input("Enter the limit up to which you want to generate prime numbers: "))
                primes = generate_primes_up_to(limit)
                print(f"Prime numbers up to {limit}: {primes[:10]}...")  # Show only first 10 primes to avoid flooding output
            except ValueError:
                print("You entered an invalid number. Please enter an integer.")
        
        elif choice == '3':
            try:
                limit = int(input("Enter the limit up to which you want to generate prime numbers: "))
                primes = generate_primes_up_to(limit)
                export_to_csv(primes)  # Export to CSV
            except ValueError:
                print("You entered an invalid number. Please enter an integer.")
        
        elif choice == '4':
            try:
                limit = int(input("Enter the limit up to which you want to generate prime numbers: "))
                primes = generate_primes_up_to(limit)
                export_to_pdf(primes)  # Export to PDF
            except ValueError:
                print("You entered an invalid number. Please enter an integer.")
        
        elif choice == '5':
            print("Exiting program.")
            break  # Exit the program

        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
