import markdown2

class MarkdownProcessor:
    def process_markdown(self, markdown_content):
        # Convert Markdown to HTML using markdown2
        html_content = markdown2.markdown(markdown_content, extras=['fenced-code-blocks', 'tables', 'header-ids'])
        return html_content
