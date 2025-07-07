# markdown-to-pdf-exporter/src/main.py

import os
from exporters.pdf_exporter import PdfExporter
from utils.config_loader import load_config, resolve_paths, resolve_book_structure_paths

def main():
    # Set project root path based on current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Parent directory of src
    
    # Configuration file paths
    export_config_path = os.path.join(project_root, 'config', 'export_config.yaml')
    book_structure_path = os.path.join(project_root, 'config', 'book_structure.yaml')
    
    # Load configuration files
    export_config = load_config(export_config_path)
    book_structure = load_config(book_structure_path)
    
    # Resolve paths
    export_config = resolve_paths(export_config, project_root)
    
    # Get source_root (from export_config or use project_root)
    source_root = export_config.get('source_root', project_root)
    book_structure = resolve_book_structure_paths(book_structure, source_root)
    
    # Collect markdown file list
    markdown_files = []
    
    # Get file list from book_structure
    if 'sections' in book_structure:
        for section in book_structure['sections']:
            if 'files' in section:
                markdown_files.extend(section['files'])
    
    # Include files from export_config if available
    if 'include_markdown_files' in export_config:
        markdown_files.extend(export_config['include_markdown_files'])
    
    # Remove duplicates
    markdown_files = list(dict.fromkeys(markdown_files))
    
    print(f"Project root: {project_root}")
    print(f"Source root: {source_root}")
    print(f"Number of markdown files to process: {len(markdown_files)}")
    
    # Check for missing files
    missing_files = []
    for file_path in markdown_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Warning: The following files could not be found:")
        for missing_file in missing_files:
            print(f"  - {missing_file}")
    
    # Initialize PDF exporter and execute
    pdf_exporter = PdfExporter(export_config)
    output_file = export_config['output_file']
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Export to PDF
    pdf_exporter.export_to_pdf(markdown_files, output_file)

if __name__ == "__main__":
    main()