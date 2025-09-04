import gzip
import os

input_folder = 'web_interface'    # folder with web files
output_folder = 'converted_h'     # folder to save .h files

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def convert_file(input_path, relpath):
    file_name = os.path.basename(input_path)
    base_name, ext = os.path.splitext(relpath)

    with open(input_path, 'rb') as f:
        content = f.read()

    gzipped = gzip.compress(content, compresslevel=9)

    # sanitize for C variable naming
    c_name = relpath.replace('/', '_').replace('.', '_') + '_gz'

    h_content = f'const unsigned char {c_name}[] PROGMEM = {{\n'
    for i, b in enumerate(gzipped):
        if i % 12 == 0:
            h_content += '\n '
        h_content += f'0x{b:02x}, '
    h_content = h_content.rstrip(', ') + '\n};\n'
    h_content += f'const unsigned int {c_name}_len = {len(gzipped)};\n'

    # Save in output folder, flattening directory names into underscores
    safe_name = relpath.replace('/', '_').replace('.', '_') + '_gz.h'
    output_file = os.path.join(output_folder, safe_name)

    with open(output_file, 'w') as f:
        f.write(h_content)
    
    print(f'[+] Converted {relpath} → {output_file}')

# Walk through all files in web_interface + subdirectories
for root, dirs, files in os.walk(input_folder):
    for file in files:
        # Only convert HTML, CSS, JS (leave .lang & .json untouched)
        if file.endswith(('.html', '.css', '.js')):
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, input_folder)  # keep subdir info
            convert_file(filepath, relpath)

print(f"\nAll files converted (excluding .lang and .json) → '{output_folder}' folder ready for ESP flash.")
