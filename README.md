# Markdown to Ebook

This project provides a simple and efficient way to convert Markdown documents into a single PDF file, suitable for creating eBooks or documentation.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [License](#license)

## Features

- Convert multiple Markdown files into a single PDF document.
- Customizable PDF layout using HTML templates and CSS styles.
- Easy configuration through YAML files.
- Supports various Markdown features.

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

1. **Set source root path**: Modify the `source_root` field in the `config/export_config.yaml` file to specify the root directory where your markdown files are located.

   ```yaml
   source_root: /home/harimkang/workspace/ai-engineer-guide
   ```

2. **Define book structure**: Modify the `config/book_structure.yaml` file to define the order and structure of markdown files to be included in the PDF.

3. **Execute PDF conversion**: Run the main script to generate the PDF.

```bash
python src/main.py
```

## Configuration

Configuration files are located in the `config/` directory:

- `export_config.yaml`: PDF conversion settings (page size, margins, output path, source root path, etc.)
- `book_structure.yaml`: Defines the book structure and order of markdown files to include

### export_config.yaml Key Settings

- `source_root`: Absolute path to the root directory containing markdown files
- `page_size`: PDF page size (A4, Letter, etc.)
- `margins`: Page margin settings (top, bottom, left, right)
- `output_file`: Path for the generated PDF file
- `template`: HTML template file path
- `css`: CSS stylesheet file path

## License

This project is licensed under the MIT License. See the LICENSE file for more details.