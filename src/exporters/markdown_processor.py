import markdown2
import re

class MarkdownProcessor:
    def process_markdown(self, markdown_content):
        # Remove YAML front matter if present
        markdown_content = self.remove_yaml_frontmatter(markdown_content)
        
        # Convert Markdown to HTML using markdown2
        html_content = markdown2.markdown(markdown_content, extras=['fenced-code-blocks', 'tables', 'header-ids'])
        return html_content
    
    def remove_yaml_frontmatter(self, content):
        """
        Remove YAML front matter from markdown content.
        
        YAML front matter is typically delimited by --- at the beginning and end:
        ---
        title: "Some Title"
        date: "2025-07-02"
        ---
        
        Args:
            content: Raw markdown content that may contain YAML front matter
            
        Returns:
            Markdown content with YAML front matter removed
        """
        # Pattern to match YAML front matter
        # ^--- starts at beginning of file
        # .*? matches any content (non-greedy)
        # ^--- matches closing delimiter on a new line
        pattern = r'^---\s*\n.*?\n---\s*\n'
        
        # Remove the front matter using regex with DOTALL flag to match newlines
        cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # Remove any leading whitespace that might be left
        cleaned_content = cleaned_content.lstrip()
        
        return cleaned_content
