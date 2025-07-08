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
- Supports various Markdown features including code blocks and tables.
- Supports various mermaid graphs and charts.
- **Automatically removes YAML front matter** from markdown files (e.g., metadata headers with title, date, tags).
- Interactive mode for easy setup.
- Command-line interface for automation and scripting.
- Font size customization (small, medium, large, or custom sizes).
- Professional PDF styling with title pages and proper sectioning.

## Installation

To install the required dependencies, run:

```bash
uv sync

# OR
pip install -r requirements.txt

# For Mermaid build
playwright install chromium
```

## Usage

The tool provides both interactive and command-line interfaces:

### Interactive Mode (Recommended for first-time users)

Simply run the script without any arguments to enter interactive mode:

```bash
python src/main.py
```

This will guide you through:
- Setting book title and author
- Specifying the source directory path
- Choosing output file location
- Automatically generating configuration files and PDF

### Command-line Options

#### 1. Generate Configuration Files

Automatically scan a directory for markdown files and generate configuration files:

```bash
python src/main.py --path <DOCS-PATH> --build
```

With custom title and author:

```bash
python src/main.py --path <DOCS-PATH> --build --title "My E-Book" --author "John Doe"
```

This will:
- Scan the specified directory for markdown files
- Generate `config/book_structure.yaml` based on directory structure
- Generate `config/export_config.yaml` with default settings

#### 2. Export PDF from Existing Configuration

Export PDF using existing configuration files:

```bash
python src/main.py --export output/ebook.pdf
```

This will:
- Read existing configuration files from `config/` directory
- Generate PDF at the specified location

#### 3. Generate Configuration and Export in One Command

Combine both operations in a single command:

```bash
python src/main.py --path <DOCS-PATH> --build --export output/ebook.pdf
```

This will:
- Generate configuration files from the specified directory
- Immediately export PDF to the specified location

### Command-line Options

- `--path PATH`: Specify the root directory containing markdown files (required with `--build`)
- `--build`: Generate configuration files based on directory structure
- `--export OUTPUT_FILE`: Export PDF to the specified file location
- `--title TITLE`: Specify book title (used with `--build`)
- `--author AUTHOR`: Specify book author (used with `--build`)

**Note**: Running without arguments launches interactive mode. Otherwise, at least one of `--build` or `--export` must be specified.

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

### Markdown Processing

The tool automatically handles various Markdown features:

- **YAML Front Matter Removal**: Files with YAML front matter (metadata headers) are automatically processed to remove the header before conversion:
  ```markdown
  ---
  title: "Document Title"
  date: "2025-07-02"
  tags: ["tag1", "tag2"]
  difficulty: "medium"
  ---
  
  # Your content starts here
  ```
  The YAML front matter (between `---` delimiters) will be automatically removed from the PDF output.

- **Code Blocks**: Syntax highlighting and proper formatting
- **Tables**: Full table support with styling
- **Headers**: Automatic header ID generation for internal linking
- **Lists**: Ordered and unordered lists with proper styling

## License

This project is licensed under the MIT License. See the LICENSE file for more details.