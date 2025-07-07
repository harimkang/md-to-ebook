import os
import yaml

def load_config(config_file):
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def resolve_paths(config, project_root):
    """
    Converts relative paths in the configuration file to absolute paths.
    
    Args:
        config: Loaded configuration dictionary
        project_root: Project root path
        
    Returns:
        Configuration dictionary with resolved paths
    """
    resolved_config = config.copy()
    
    # Use source_root if configured, otherwise use project_root
    source_root = config.get('source_root', project_root)
    
    # Resolve template and CSS file paths relative to project_root
    if 'template' in resolved_config:
        if not os.path.isabs(resolved_config['template']):
            resolved_config['template'] = os.path.join(project_root, resolved_config['template'])
    
    if 'css' in resolved_config:
        if not os.path.isabs(resolved_config['css']):
            resolved_config['css'] = os.path.join(project_root, resolved_config['css'])
    
    # Resolve output file path relative to project_root
    if 'output_file' in resolved_config:
        if not os.path.isabs(resolved_config['output_file']):
            resolved_config['output_file'] = os.path.join(project_root, resolved_config['output_file'])
    
    # Resolve markdown files relative to source_root
    if 'include_markdown_files' in resolved_config:
        resolved_files = []
        for file_path in resolved_config['include_markdown_files']:
            if not os.path.isabs(file_path):
                resolved_files.append(os.path.join(source_root, file_path))
            else:
                resolved_files.append(file_path)
        resolved_config['include_markdown_files'] = resolved_files
    
    return resolved_config

def resolve_book_structure_paths(book_structure, source_root):
    """
    Converts file paths in book_structure.yaml to absolute paths.
    
    Args:
        book_structure: Loaded book structure dictionary
        source_root: Source root path
        
    Returns:
        Book structure dictionary with resolved paths
    """
    resolved_structure = book_structure.copy()
    
    if 'sections' in resolved_structure:
        for section in resolved_structure['sections']:
            if 'files' in section:
                resolved_files = []
                for file_path in section['files']:
                    if not os.path.isabs(file_path):
                        resolved_files.append(os.path.join(source_root, file_path))
                    else:
                        resolved_files.append(file_path)
                section['files'] = resolved_files
    
    return resolved_structure