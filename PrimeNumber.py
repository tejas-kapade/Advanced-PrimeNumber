import math
import time
import csv
from tqdm import tqdm  # Import tqdm for progress bar
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

# Function to export primes to a CSV file
def export_to_csv(primes, filename="primes.csv"):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Prime Numbers"])
            for prime in primes:
                writer.writerow([prime])
        print(f"Prime numbers have been saved to {filename}.")
    except Exception as e:
        print(f"Error while saving to CSV: {e}")

# Function to export primes to a PDF file
def export_to_pdf(primes, filename="primes.pdf"):
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica", 10)
        c.drawString(30, 750, "Prime Numbers:")
        
        y_position = 730  # Starting position for the primes

        for i, prime in enumerate(primes):
            if y_position <= 50:  # Check if space on page is running out
                c.showPage()
                c.setFont("Helvetica", 10)
                c.drawString(30, 750, "Prime Numbers:")
                y_position = 730  # Reset the y position for a new page

            c.drawString(30, y_position, str(prime))
            y_position -= 12  # Move down for the next prime number

        c.save()
        print(f"Prime numbers have been saved to {filename}.")
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
