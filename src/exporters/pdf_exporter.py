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
        else:
            # Use default template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>AI Engineer Guide</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1, h2, h3 { color: #333; }
                    code { background-color: #f4f4f4; padding: 2px 4px; }
                    pre { background-color: #f4f4f4; padding: 10px; overflow-x: auto; }
                </style>
            </head>
            <body>
                {{ content }}
            </body>
            </html>
            """

        # Combine the template with the HTML content
        final_html = template.replace("{{ content }}", html_content)

        # Generate the PDF with CSS if available
        html_doc = HTML(string=final_html)
        if self.css_path and os.path.exists(self.css_path):
            html_doc.write_pdf(output_path, stylesheets=[self.css_path])
        else:
            html_doc.write_pdf(output_path)

        print(f"PDF successfully generated: {output_path}")