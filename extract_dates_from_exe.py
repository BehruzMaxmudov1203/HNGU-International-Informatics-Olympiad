import re

# Path to the binary file
binary_path = 'c:/Users/Behruz/Desktop/Turk_man/File_zip_extracted/Project1.exe'

# Readable ASCII string extraction
MIN_LENGTH = 4

def extract_strings(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    result = []
    current = b''
    for b in data:
        if 32 <= b <= 126:
            current += bytes([b])
        else:
            if len(current) >= MIN_LENGTH:
                result.append(current.decode('ascii', errors='ignore'))
            current = b''
    if len(current) >= MIN_LENGTH:
        result.append(current.decode('ascii', errors='ignore'))
    return result

def main():
    strings = extract_strings(binary_path)
    date_pattern = re.compile(r'\b\d{2}\.\d{2}\.\d{4}\b')
    found_dates = set()
    for s in strings:
        for match in date_pattern.findall(s):
            found_dates.add(match)
    if found_dates:
        print('Found date(s):')
        for d in sorted(found_dates):
            print(d)
    else:
        print('No date patterns found.')

if __name__ == '__main__':
    main()
