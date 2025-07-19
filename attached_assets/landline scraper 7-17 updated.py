import csv
import re

# Aggressively expanded list of known landline prefixes (NPA-NXX)
LANDLINE_PREFIXES = {
    "205-222", "205-333", "212-222", "305-222", "407-222", "415-222", "713-222", 
    "312-222", "404-222", "503-222", "602-222", "702-222", "818-222", "919-222",
    "646-346", "718-455", "718-599", "914-220", "310-454", "212-555", "917-324", "516-466",
    "847-555", "630-620", "773-522", "312-698", "708-682", "815-759", "847-329",
    "203-234", "315-448", "518-474", "570-387", "631-444", "716-848", "718-422", "845-334",
    "860-486", "914-255", "978-658", "212-970", "214-220", "312-906", "512-465", "713-465",
    "972-465", "202-785", "305-810", "407-814", "504-861", "602-627", "702-486", "808-586"
}

# Common toll-free numbers
TOLL_FREE_PREFIXES = {"800", "888", "877", "866", "855", "844", "833", "822"}

# Common VOIP area codes
VOIP_AREA_CODES = {"347", "646", "650", "678", "702", "704", "716", "818", "919"}

def clean_number_format(number):
    """Removes formatting to standardize phone numbers and extract NPA-NXX."""
    if "x" in number.lower() or "ext" in number.lower():
        return None, None  # Assume landline if it has an extension
    
    cleaned = re.sub(r"[^\d]", "", number)  # Remove non-numeric characters
    if len(cleaned) == 10:  # Standard US number (without country code)
        return f"{cleaned[:3]}-{cleaned[3:6]}", cleaned[:3]
    elif len(cleaned) == 11 and cleaned.startswith("1"):  # US number with country code
        return f"{cleaned[1:4]}-{cleaned[4:7]}", cleaned[1:4]
    return None, None  # Skip invalid numbers

def load_data(input_file):
    """
    Loads data from a CSV file.
    Detects the column with "phone" in its header (case-insensitive)
    and returns headers, data rows, and the phone column index.
    """
    data = []
    with open(input_file, "r", newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if headers is None:
            print("Error: The CSV file is empty or missing headers.")
            return [], [], None
        
        # Normalize headers to lower case and strip spaces
        normalized_headers = [h.strip().lower() for h in headers]
        phone_index = next((i for i, h in enumerate(normalized_headers) if "phone" in h), None)
        
        if phone_index is None:
            print("Error: Could not find a column with 'phone' in the header.")
            return headers, [], None
        
        for row in reader:
            if len(row) > phone_index:  # Only include rows with enough columns
                data.append(row)
    return headers, data, phone_index

def filter_landlines(data, phone_index):
    """
    Filters out rows where the phone number appears to be a landline,
    toll-free, or VOIP number. Returns the rows that pass the filter.
    """
    filtered_data = []
    debug_count = 0
    max_debug = 30  # Limit debug messages

    for row in data:
        phone_number = row[phone_index].strip()
        prefix, area_code = clean_number_format(phone_number)
        
        if debug_count < max_debug:
            print(f"Checking number: {phone_number} -> Prefix: {prefix}, Area Code: {area_code}")
            debug_count += 1
        
        if (prefix and prefix not in LANDLINE_PREFIXES and 
            area_code not in TOLL_FREE_PREFIXES and 
            area_code not in VOIP_AREA_CODES):
            filtered_data.append(row)
        elif debug_count < max_debug:
            print(f"Filtered out: {phone_number}")
    
    return filtered_data

def save_to_csv(output_file, headers, data):
    """Saves the headers and data rows to a CSV file."""
    # Using all rows as-is; you can remove duplicates if needed.
    with open(output_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

def main():
    input_file = "C:/Users/14074/Downloads/alabama.athlete.leads.0.5k.csv"  # Update with your CSV file path
    output_file = "filtered_numbers.csv"
    
    headers, data, phone_index = load_data(input_file)
    if phone_index is None:
        return  # Stop execution if no phone column was found
    
    cleaned_data = filter_landlines(data, phone_index)
    save_to_csv(output_file, headers, cleaned_data)
    
    print(f"Processing complete! {len(cleaned_data)} rows saved to {output_file}")

if __name__ == "__main__":
    main()