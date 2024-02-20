from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_svg(input_file, output_directory):
    with open(input_file, 'r') as f:
        content = f.read()
        width_match = re.search(r'width="([^"]*)"', content)
        height_match = re.search(r'height="([^"]*)"', content)
        width = width_match.group(1) if width_match else ''
        height = height_match.group(1) if height_match else ''

    max_size_kb = 14
    current_file_size = 0
    file_counter = 1
    current_output_file = "{}/{}_{}.svg".format(output_directory, os.path.splitext(os.path.basename(input_file))[0], file_counter)
    line_count = 0

    os.makedirs(output_directory, exist_ok=True)

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
                current_output_file = "{}/{}_{}.svg".format(output_directory, os.path.splitext(os.path.basename(input_file))[0], file_counter)
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
        current_output_file = "{}/{}_{}.svg".format(output_directory, os.path.splitext(os.path.basename(input_file))[0], i)
        with open(current_output_file, 'a') as output_f:
            if not output_f.read().endswith('</svg>\n'):
                output_f.write('</svg>\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file and allowed_file(file.filename):
            # Save the uploaded file
            uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(uploaded_file_path)

            # Process the SVG file
            output_directory = os.path.join(app.config['OUTPUT_FOLDER'], os.path.splitext(file.filename)[0])
            process_svg(uploaded_file_path, output_directory)

            return redirect(url_for('download', filename=os.path.splitext(file.filename)[0]))

        else:
            return render_template('index.html', error='Invalid file type. Only SVG files are allowed.')

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return render_template('download.html', filename=filename)

@app.route('/outputs/<filename>/<int:file_number>')
def processed_file(filename, file_number):
    output_directory = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_from_directory(output_directory, '{}_{}.svg'.format(filename, file_number))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)
