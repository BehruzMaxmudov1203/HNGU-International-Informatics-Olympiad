import re
from collections import Counter

# Read the RTF file as text
with open('Annex9/Magtymguly_Shifrlenen_1000.rtf', 'r', encoding='utf-8', errors='ignore') as f:
    rtf = f.read()

# Extract all Unicode escape sequences (e.g., \'uXXXX?)
# RTF Unicode: \\uN? where N is a signed 16-bit integer
unicodes = re.findall(r'\\u(-?\d+)', rtf)
if not unicodes:
    # Try to extract all non-ASCII characters as fallback
    chars = [c for c in rtf if ord(c) > 127]
    codes = [ord(c) for c in chars]
else:
    codes = [int(u) for u in unicodes]

# Find the most common code (likely space or a common letter)
if not codes:
    print('No Unicode codes found.')
    exit(1)

counter = Counter(codes)
most_common_code, _ = counter.most_common(1)[0]

# Assume the original text's most common character is space (U+0020)
# k = encrypted_code - original_code
k = most_common_code - 32
print(k)
