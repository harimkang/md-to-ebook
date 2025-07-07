# markdown-to-pdf-exporter/src/main.py

import os
import argparse
import yaml
from exporters.pdf_exporter import PdfExporter
from utils.config_loader import load_config, resolve_paths, resolve_book_structure_paths

def scan_markdown_files(root_path):
    """
    Scan a directory for markdown files and organize them by structure.
    
    Args:
        root_path: Root directory to scan for markdown files
        
    Returns:
        List of markdown files organized by directory structure
    """
    markdown_files = []
    docs_path = os.path.join(root_path, 'docs')
    
    if not os.path.exists(docs_path):
        print(f"Warning: docs directory not found at {docs_path}")
        return []
    
    # Walk through the docs directory
    for root, dirs, files in os.walk(docs_path):
        # Sort directories and files for consistent ordering
        dirs.sort()
        files.sort()
        
        for file in files:
            if file.endswith('.md'):
                relative_path = os.path.relpath(os.path.join(root, file), root_path)
                markdown_files.append(relative_path)
    
    return sorted(markdown_files)

def generate_book_structure(root_path, markdown_files, title=None, author=None):
    """
    Generate book structure configuration based on markdown files.
    
    Args:
        root_path: Root directory path
        markdown_files: List of markdown files
        title: Book title (optional)
        author: Book author (optional)
        
    Returns:
        Dictionary representing book structure
    """
    sections = {}
    
    for file_path in markdown_files:
        # Extract section from path
        parts = file_path.split(os.sep)
        if len(parts) >= 3 and parts[0] == 'docs':
            section_dir = parts[1]
            # Extract section title from directory name
            if '-' in section_dir:
                section_parts = section_dir.split('-', 1)
                if len(section_parts) > 1:
                    section_title = section_parts[1].replace('-', ' ').title()
                else:
                    section_title = section_dir.replace('-', ' ').title()
            else:
                section_title = section_dir.replace('-', ' ').title()
            
            if section_title not in sections:
                sections[section_title] = []
            sections[section_title].append(file_path)
    
    # Convert to the expected format
    book_structure = {
        'title': title or 'Title of the Book',
        'author': author or 'Author Name',
        'sections': []
    }
    
    for title, files in sections.items():
        book_structure['sections'].append({
            'title': title,
            'files': sorted(files)
        })
    
    return book_structure

def generate_export_config(root_path, output_file=None, font_size=None):
    """
    Generate export configuration.
    
    Args:
        root_path: Root directory path
        output_file: Output PDF file path
        font_size: Base font size (e.g., 'small', 'medium', 'large', or specific size like '14pt')
        
    Returns:
        Dictionary representing export configuration
    """
    if output_file is None:
        output_file = 'output/ebook.pdf'
    
    # Font size presets
    font_presets = {
        'small': {
            'base_font_size': '10pt',
            'line_height': '1.5',
            'h1_size': '20pt',
            'h2_size': '16pt',
            'h3_size': '14pt',
            'code_size': '9pt'
        },
        'medium': {
            'base_font_size': '12pt',
            'line_height': '1.6',
            'h1_size': '24pt',
            'h2_size': '20pt',
            'h3_size': '16pt',
            'code_size': '10pt'
        },
        'large': {
            'base_font_size': '14pt',
            'line_height': '1.7',
            'h1_size': '28pt',
            'h2_size': '24pt',
            'h3_size': '18pt',
            'code_size': '12pt'
        }
    }
    
    # Determine font settings
    if font_size and font_size in font_presets:
        font_settings = font_presets[font_size]
    elif font_size and font_size.endswith('pt'):
        # Custom font size
        base_size = int(font_size[:-2])
        font_settings = {
            'base_font_size': font_size,
            'line_height': '1.6',
            'h1_size': f'{base_size + 12}pt',
            'h2_size': f'{base_size + 8}pt',
            'h3_size': f'{base_size + 4}pt',
            'code_size': f'{max(base_size - 2, 8)}pt'
        }
    else:
        # Default medium
        font_settings = font_presets['medium']
    
    return {
        'page_size': 'A4',
        'margins': {
            'top': 20,
            'bottom': 20,
            'left': 15,
            'right': 15
        },
        'output_file': output_file,
        'template': 'src/templates/pdf_template.html',
        'css': 'src/templates/styles.css',
        'source_root': root_path,
        'font_settings': font_settings
    }

def build_config_files(source_path, output_file=None, title=None, author=None, font_size=None):
    """
    Build configuration files based on source path.
    
    Args:
        source_path: Path to scan for markdown files
        output_file: Optional output file path
        title: Book title (optional)
        author: Book author (optional)
        font_size: Font size preset or custom size (optional)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    print(f"Scanning markdown files in: {source_path}")
    
    # Scan for markdown files
    markdown_files = scan_markdown_files(source_path)
    
    if not markdown_files:
        print("No markdown files found!")
        return False
    
    print(f"Found {len(markdown_files)} markdown files")
    
    # Generate configurations
    book_structure = generate_book_structure(source_path, markdown_files, title, author)
    export_config = generate_export_config(source_path, output_file, font_size)
    
    # Ensure config directory exists
    config_dir = os.path.join(project_root, 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # Write book_structure.yaml
    book_structure_path = os.path.join(config_dir, 'book_structure.yaml')
    with open(book_structure_path, 'w', encoding='utf-8') as f:
        yaml.dump(book_structure, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    # Write export_config.yaml
    export_config_path = os.path.join(config_dir, 'export_config.yaml')
    with open(export_config_path, 'w', encoding='utf-8') as f:
        yaml.dump(export_config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print("Generated configuration files:")
    print(f"  - {book_structure_path}")
    print(f"  - {export_config_path}")
    
    return True

def export_pdf(output_file=None):
    """
    Export PDF based on existing configuration files.
    
    Args:
        output_file: Optional output file path to override config
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Configuration file paths
    export_config_path = os.path.join(project_root, 'config', 'export_config.yaml')
    book_structure_path = os.path.join(project_root, 'config', 'book_structure.yaml')
    
    # Check if config files exist
    if not os.path.exists(export_config_path):
        print(f"Error: Configuration file not found: {export_config_path}")
        print("Please run with --build option first to generate configuration files.")
        return False
    
    if not os.path.exists(book_structure_path):
        print(f"Error: Configuration file not found: {book_structure_path}")
        print("Please run with --build option first to generate configuration files.")
        return False
     # Load configuration files
    export_config = load_config(export_config_path)
    book_structure = load_config(book_structure_path)

    # Ensure title and author from book_structure are in export_config
    if 'title' in book_structure and 'title' not in export_config:
        export_config['title'] = book_structure['title']
    if 'author' in book_structure and 'author' not in export_config:
        export_config['author'] = book_structure['author']

    # Override output file if specified
    if output_file:
        export_config['output_file'] = output_file
    
    # Resolve paths
    export_config = resolve_paths(export_config, project_root)
    
    # Get source_root (from export_config or use project_root)
    source_root = export_config.get('source_root', project_root)
    book_structure = resolve_book_structure_paths(book_structure, source_root)
    
    # Collect markdown files with section information
    sections_with_files = []
    total_files = 0
    
    # Get sections and files from book_structure
    if 'sections' in book_structure:
        for section in book_structure['sections']:
            if 'files' in section:
                sections_with_files.append({
                    'title': section.get('title', 'Untitled Section'),
                    'files': section['files']
                })
                total_files += len(section['files'])
    
    print(f"Project root: {project_root}")
    print(f"Source root: {source_root}")
    print(f"Number of sections: {len(sections_with_files)}")
    print(f"Total markdown files to process: {total_files}")
    
    # Check for missing files
    missing_files = []
    for section in sections_with_files:
        for file_path in section['files']:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
    
    if missing_files:
        print("Warning: The following files could not be found:")
        for missing_file in missing_files:
            print(f"  - {missing_file}")
    
    # Initialize PDF exporter and execute
    pdf_exporter = PdfExporter(export_config)
    final_output_file = export_config['output_file']
    
    # Create output directory
    os.makedirs(os.path.dirname(final_output_file), exist_ok=True)
    
    # Export to PDF with section structure
    pdf_exporter.export_to_pdf_with_sections(sections_with_files, final_output_file)
    
    return True

def interactive_mode():
    """
    Interactive mode for setting up book configuration and generating PDF.
    """
    print("=" * 60)
    print("📚 Markdown to PDF Converter - Interactive Mode")
    print("=" * 60)
    print()
    
    # Get book information
    print("📖 Book Information:")
    title = input("Enter book title [Title of the Book]: ").strip()
    if not title:
        title = "Title of the Book"
    
    author = input("Enter author name [Author Name]: ").strip()
    if not author:
        author = "Author Name"
    
    print()
    
    # Get source path
    print("📁 Source Configuration:")
    while True:
        source_path = input("Enter path to markdown files directory: ").strip()
        if not source_path:
            print("❌ Path cannot be empty. Please enter a valid path.")
            continue
        
        # Expand user path if needed
        source_path = os.path.expanduser(source_path)
        
        if not os.path.exists(source_path):
            print(f"❌ Path does not exist: {source_path}")
            continue
            
        docs_path = os.path.join(source_path, 'docs')
        if not os.path.exists(docs_path):
            print(f"❌ 'docs' directory not found in: {source_path}")
            continue
            
        break
    
    print()
    
    # Get output file
    print("📄 Output Configuration:")
    output_file = input("Enter output PDF file name [output/ebook.pdf]: ").strip()
    if not output_file:
        output_file = "output/ebook.pdf"
    
    print()
    
    # Get font size preference
    print("🔤 Font Size:")
    print("1. Small (10pt) [default]")
    print("2. Medium (12pt)")
    print("3. Large (14pt)")
    print("4. Custom size")
    
    font_choice = input("Select font size [2]: ").strip()
    font_size = None
    
    if font_choice == '1':
        font_size = 'small'
    elif font_choice == '2':
        font_size = 'medium'
    elif font_choice == '3':
        font_size = 'large'
    elif font_choice == '4':
        custom_size = input("Enter custom font size (e.g., 15pt): ").strip()
        if custom_size and custom_size.endswith('pt'):
            font_size = custom_size
        else:
            print("Invalid format, using small size")
            font_size = 'small'
    else:
        font_size = 'small'
    
    print()
    print("🔄 Processing...")
    print(f"   Title: {title}")
    print(f"   Author: {author}")
    print(f"   Source: {source_path}")
    print(f"   Output: {output_file}")
    print(f"   Font Size: {font_size}")
    print()
    
    # Build configuration files
    try:
        success = build_config_files(source_path, output_file, title, author, font_size)
        if not success:
            print("❌ Failed to build configuration files.")
            return False
        
        print("✅ Configuration files generated successfully!")
        print()
        
        # Ask if user wants to generate PDF immediately
        generate_pdf = input("Generate PDF now? [Y/n]: ").strip().lower()
        if generate_pdf in ['', 'y', 'yes']:
            print("🔄 Generating PDF...")
            success = export_pdf(output_file)
            if success:
                print("✅ PDF generated successfully!")
            else:
                print("❌ Failed to generate PDF.")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def validate_path(path):
    """
    Validate if the given path exists and contains a docs directory.
    
    Args:
        path: Path to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(path):
        return False
    
    docs_path = os.path.join(path, 'docs')
    return os.path.exists(docs_path)

def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown documents to PDF ebook',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (run without arguments)
  python src/main.py
  
  # Generate config files from markdown directory
  python src/main.py --path /path/to/markdown/root --build
  
  # Generate config with custom title and author
  python src/main.py --path /path/to/markdown/root --build --title "My Book" --author "John Doe"
  
  # Generate config with large font size
  python src/main.py --path /path/to/markdown/root --build --font-size large
  
  # Export PDF using existing config files  
  python src/main.py --export output/ebook.pdf
  
  # Generate config and export PDF in one command
  python src/main.py --path /path/to/markdown/root --build --export output/ebook.pdf
        """
    )
    
    parser.add_argument('--path', 
                       help='Path to the root directory containing markdown files')
    parser.add_argument('--build', 
                       action='store_true',
                       help='Generate configuration files based on markdown directory structure')
    parser.add_argument('--export', 
                       metavar='OUTPUT_FILE',
                       help='Export PDF to specified file (uses config if no file specified)')
    parser.add_argument('--title',
                       help='Book title (used with --build)')
    parser.add_argument('--author',
                       help='Book author (used with --build)')
    parser.add_argument('--font-size',
                       choices=['small', 'medium', 'large'],
                       help='Font size preset: small (10pt), medium (12pt), large (14pt) (used with --build)')
    
    args = parser.parse_args()
    
    # If no arguments provided, run interactive mode
    if not any([args.path, args.build, args.export]):
        return 0 if interactive_mode() else 1
    
    # Validate arguments
    if args.build and not args.path:
        parser.error("--build requires --path to be specified")
    
    if not args.build and not args.export:
        parser.error("At least one of --build or --export must be specified")
    
    if (args.title or args.author or args.font_size) and not args.build:
        parser.error("--title, --author, and --font-size can only be used with --build")
    
    success = True
    
    # Build configuration files if requested
    if args.build:
        if not os.path.exists(args.path):
            print(f"Error: Path does not exist: {args.path}")
            return 1
        
        if not validate_path(args.path):
            print(f"Error: Invalid path. Directory must contain a 'docs' subdirectory: {args.path}")
            return 1
        
        output_file = args.export if args.export else None
        success = build_config_files(args.path, output_file, args.title, args.author, args.font_size)
        
        if not success:
            return 1
    
    # Export PDF if requested
    if args.export:
        success = export_pdf(args.export)
        
        if not success:
            return 1
    
    print("Operation completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())