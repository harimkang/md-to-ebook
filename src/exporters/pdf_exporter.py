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