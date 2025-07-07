import os
from weasyprint import HTML
from .markdown_processor import MarkdownProcessor

class PdfExporter:
    def __init__(self, config):
        self.config = config
        self.template_path = config.get('template')
        self.css_path = config.get('css')

    def export_to_pdf(self, markdown_files, output_path):
        # Initialize the Markdown processor
        processor = MarkdownProcessor()

        # Process each Markdown file and convert to HTML
        html_content = ""
        for md_file in markdown_files:
            if os.path.exists(md_file):
                with open(md_file, 'r', encoding='utf-8') as file:
                    md_content = file.read()
                html_content += processor.process_markdown(md_content) + "<div style='page-break-after: always;'></div>"
            else:
                print(f"Warning: Markdown file not found: {md_file}")
                continue

        # Load the HTML template
        if self.template_path and os.path.exists(self.template_path):
            with open(self.template_path, 'r', encoding='utf-8') as template_file:
                template = template_file.read()
            
            # Replace template variables with actual values
            title = self.config.get('title', 'Title of the Book')
            author = self.config.get('author', 'Author Name')
            template = template.replace('{{ title }}', title)
            template = template.replace('{{ author }}', author)
        else:
            # Use default template
            font_settings = self.config.get('font_settings', {})
            base_font_size = font_settings.get('base_font_size', '12pt')
            line_height = font_settings.get('line_height', '1.6')
            h1_size = font_settings.get('h1_size', '24pt')
            h2_size = font_settings.get('h2_size', '20pt')
            h3_size = font_settings.get('h3_size', '16pt')
            code_size = font_settings.get('code_size', '10pt')
            
            # Get title and author from config, with fallbacks
            title = self.config.get('title', 'Title of the Book')
            author = self.config.get('author', 'Author Name')
            
            template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{title}</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 20px; 
                        font-size: {base_font_size};
                        line-height: {line_height};
                    }}
                    .title-page {{
                        text-align: center;
                        margin-bottom: 50px;
                        padding: 50px 0;
                        border-bottom: 2px solid #333;
                    }}
                    .title-page h1 {{
                        font-size: {h1_size};
                        margin-bottom: 20px;
                        color: #333;
                    }}
                    .title-page .author {{
                        font-size: {h2_size};
                        color: #666;
                        font-style: italic;
                    }}
                    h1 {{ color: #333; font-size: {h1_size}; }}
                    h2 {{ color: #333; font-size: {h2_size}; }}
                    h3 {{ color: #333; font-size: {h3_size}; }}
                    code {{ 
                        background-color: #f4f4f4; 
                        padding: 2px 4px; 
                        font-size: {code_size};
                    }}
                    pre {{ 
                        background-color: #f4f4f4; 
                        padding: 10px; 
                        overflow-x: auto;
                        font-size: {code_size};
                    }}
                </style>
            </head>
            <body>
                <div class="title-page">
                    <h1>{title}</h1>
                    <div class="author">by {author}</div>
                </div>
                {{{{ content }}}}
            </body>
            </html>
            """

        # Apply font settings to existing template if configured
        font_settings = self.config.get('font_settings', {})
        if font_settings:
            template = self.apply_font_settings_to_template(template, font_settings)

        # Combine the template with the HTML content
        final_html = template.replace("{{ content }}", html_content)

        # Generate the PDF with CSS if available
        html_doc = HTML(string=final_html)
        if self.css_path and os.path.exists(self.css_path):
            html_doc.write_pdf(output_path, stylesheets=[self.css_path])
        else:
            html_doc.write_pdf(output_path)

        print(f"PDF successfully generated: {output_path}")

    def export_to_pdf_with_sections(self, sections_with_files, output_path):
        """
        Export PDF with hierarchical section structure.
        
        Args:
            sections_with_files: List of dictionaries with 'title', 'type', and 'files' keys
            output_path: Output PDF file path
        """
        # Initialize the Markdown processor
        processor = MarkdownProcessor()

        # Get source root from config to resolve file paths
        source_root = self.config.get('source_root', '')
        missing_files = []

        # Process each section and its files
        html_content = ""
        
        for section_info in sections_with_files:
            section_title = section_info.get('title', 'Untitled Section')
            section_type = section_info.get('type', 'section')
            section_files = section_info.get('files', [])
            
            # Add appropriate section header based on type
            if section_type == 'major_section':
                # Major section header (H2 level - under book title H1) with table of contents
                toc_html = ""
                if 'toc' in section_info and section_info['toc']:
                    toc_html = "<div class='major-section-toc'>"
                    for toc_item in section_info['toc']:
                        toc_html += f"""
                        <div class='toc-item'>
                            <div class='toc-section-title'>{toc_item['number']}. {toc_item['title']}</div>
                        </div>
                        """
                    toc_html += "</div>"
                
                html_content += f"""
                <div class="major-section-header">
                    <h2 class="major-section-title">{section_title}</h2>
                    {toc_html}
                </div>
                """
            elif section_type == 'subsection':
                # Subsection header (H3 level - under major section H2)
                html_content += f"""
                <div class="subsection-header">
                    <h3 class="subsection-title">{section_title}</h3>
                </div>
                """
            else:
                # Regular section header (backward compatibility - H2 level)
                html_content += f"""
                <div class="section-header">
                    <h2 class="section-title">{section_title}</h2>
                </div>
                """
            
            # Process each file in the section (only if there are files)
            if section_files:
                for md_file in section_files:
                    if os.path.exists(md_file):
                        with open(md_file, 'r', encoding='utf-8') as file:
                            md_content = file.read()
                        
                        # Process markdown and add to content
                        file_html = processor.process_markdown(md_content)
                        html_content += file_html
                        
                        # Add page break after each file (optional)
                        html_content += "<div style='page-break-after: always;'></div>"
                    else:
                        missing_files.append(md_file)
                        continue
            
            # Add section break for major sections (new page for next major section)
            if section_type == 'major_section':
                html_content += "<div style='page-break-before: always;'></div>"

        # Report missing files
        if missing_files:
            print("Warning: The following files could not be found:")
            for file in missing_files:
                print(f"  - {file}")
            print(f"Source root: {source_root}")
            print(f"Current working directory: {os.getcwd()}")

        # Load the HTML template
        if self.template_path and os.path.exists(self.template_path):
            with open(self.template_path, 'r', encoding='utf-8') as template_file:
                template = template_file.read()
            
            # Replace template variables with actual values
            title = self.config.get('title', 'Title of the Book')
            author = self.config.get('author', 'Author Name')
            template = template.replace('{{ title }}', title)
            template = template.replace('{{ author }}', author)
        else:
            # Use default template with hierarchical sections support
            title = self.config.get('title', 'Title of the Book')
            author = self.config.get('author', 'Author Name')
            font_settings = self.config.get('font_settings', {})
            template = self._generate_default_template_with_hierarchical_sections(title, author, font_settings)

        # Apply font settings to existing template if configured
        font_settings = self.config.get('font_settings', {})
        if font_settings:
            template = self.apply_font_settings_to_template(template, font_settings)

        # Combine the template with the HTML content
        final_html = template.replace("{{ content }}", html_content)

        # Generate the PDF with CSS if available
        html_doc = HTML(string=final_html)
        if self.css_path and os.path.exists(self.css_path):
            html_doc.write_pdf(output_path, stylesheets=[self.css_path])
        else:
            html_doc.write_pdf(output_path)

        print(f"PDF successfully generated: {output_path}")
        if missing_files:
            print(f"Note: {len(missing_files)} files were missing and not included in the PDF.")
    
    def _generate_default_template_with_hierarchical_sections(self, title, author, font_settings):
        """Generate default template with hierarchical section styling support"""
        base_font_size = font_settings.get('base_font_size', '12pt')
        line_height = font_settings.get('line_height', '1.6')
        h1_size = font_settings.get('h1_size', '24pt')
        h2_size = font_settings.get('h2_size', '20pt')
        h3_size = font_settings.get('h3_size', '16pt')
        code_size = font_settings.get('code_size', '10pt')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    font-size: {base_font_size};
                    line-height: {line_height};
                }}
                .title-page {{
                    text-align: center;
                    margin-bottom: 50px;
                    padding: 100px 0;
                    border-bottom: 3px solid #333;
                    page-break-after: always;
                }}
                .title-page h1 {{
                    font-size: {h1_size};
                    margin-bottom: 30px;
                    color: #333;
                    border-bottom: none;
                    page-break-before: auto;
                    margin-top: 0;
                }}
                .title-page .author {{
                    font-size: {h2_size};
                    color: #666;
                    font-style: italic;
                    margin-top: 20px;
                }}
                /* Major section styles */
                .major-section-header {{
                    text-align: center;
                    margin: 60px 0 40px 0;
                    padding: 40px 30px;
                    border-top: 4px solid #007acc;
                    border-bottom: 2px solid #007acc;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    page-break-before: always;
                    page-break-after: avoid;
                }}
                .major-section-title {{
                    font-size: calc({h1_size} + 6pt);
                    color: #007acc;
                    margin: 0 0 30px 0;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 3px;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                }}
                /* Table of contents styles for major sections */
                .major-section-toc {{
                    text-align: left;
                    margin-top: 40px;
                    padding: 20px;
                    background-color: rgba(255, 255, 255, 0.8);
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .toc-item {{
                    margin-bottom: 15px;
                }}
                .toc-section-title {{
                    color: #007acc;
                    font-size: {h3_size};
                    margin: 0;
                    font-weight: bold;
                    padding: 10px 15px;
                    background-color: rgba(0, 122, 204, 0.1);
                    border-left: 4px solid #007acc;
                    border-radius: 4px;
                }}
                /* Subsection styles */
                .subsection-header {{
                    margin: 40px 0 20px 0;
                    padding: 20px 0;
                    border-left: 4px solid #28a745;
                    padding-left: 20px;
                    background-color: #f8f9fa;
                    page-break-after: avoid;
                }}
                .subsection-title {{
                    font-size: {h1_size};
                    color: #28a745;
                    margin: 0;
                    font-weight: bold;
                    letter-spacing: 1px;
                }}
                /* Regular section styles (backward compatibility) */
                .section-header {{
                    text-align: center;
                    margin: 50px 0;
                    padding: 30px 0;
                    border-top: 3px solid #007acc;
                    border-bottom: 1px solid #ccc;
                    page-break-before: always;
                }}
                .section-title {{
                    font-size: {h1_size};
                    color: #007acc;
                    margin: 0;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                /* Content styles - Proper hierarchy */
                h1 {{ 
                    color: #333; 
                    font-size: {h1_size}; 
                    page-break-before: avoid; 
                    margin-top: 30px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                h2 {{ 
                    color: #007acc; 
                    font-size: calc({h1_size} + 4pt);
                    margin-top: 40px;
                    margin-bottom: 25px;
                    border-bottom: 2px solid #007acc;
                    padding-bottom: 10px;
                }}
                h3 {{ 
                    color: #28a745; 
                    font-size: {h1_size};
                    margin-top: 30px;
                    margin-bottom: 20px;
                    border-left: 4px solid #28a745;
                    padding-left: 15px;
                }}
                h4 {{ 
                    color: #333; 
                    font-size: {h2_size};
                    margin-top: 25px;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                    font-weight: bold;
                }}
                h5 {{ 
                    color: #555; 
                    font-size: {h3_size};
                    margin-top: 20px;
                    margin-bottom: 10px;
                }}
                h6 {{ 
                    color: #666; 
                    font-size: calc({h3_size} - 2pt);
                    margin-top: 15px;
                    margin-bottom: 8px;
                    font-style: italic;
                }}
                code {{ 
                    background-color: #f4f4f4; 
                    padding: 2px 4px; 
                    font-size: {code_size};
                }}
                pre {{ 
                    background-color: #f4f4f4; 
                    padding: 10px; 
                    overflow-x: auto;
                    font-size: {code_size};
                }}
            </style>
        </head>
        <body>
            <div class="title-page">
                <h1>{title}</h1>
                <div class="author">by {author}</div>
            </div>
            {{{{ content }}}}
        </body>
        </html>
        """

    def apply_font_settings_to_template(self, template, font_settings):
        """
        Apply font settings to the HTML template by injecting CSS.
        
        Args:
            template: HTML template string
            font_settings: Dictionary with font configuration
            
        Returns:
            Modified template with font settings applied
        """
        base_font_size = font_settings.get('base_font_size', '12pt')
        line_height = font_settings.get('line_height', '1.6')
        h1_size = font_settings.get('h1_size', '24pt')
        h2_size = font_settings.get('h2_size', '20pt')
        h3_size = font_settings.get('h3_size', '16pt')
        code_size = font_settings.get('code_size', '10pt')
        
        # CSS to inject
        font_css = f"""
        <style>
            body {{
                font-size: {base_font_size} !important;
                line-height: {line_height} !important;
            }}
            h1 {{
                font-size: {h1_size} !important;
            }}
            h2 {{
                font-size: {h2_size} !important;
            }}
            h3 {{
                font-size: {h3_size} !important;
            }}
            h4, h5, h6 {{
                font-size: {h3_size} !important;
            }}
            code {{
                font-size: {code_size} !important;
            }}
            pre {{
                font-size: {code_size} !important;
            }}
            pre code {{
                font-size: {code_size} !important;
            }}
        </style>
        """
        
        # Insert CSS before closing head tag
        if '</head>' in template:
            template = template.replace('</head>', font_css + '\n</head>')
        
        return template