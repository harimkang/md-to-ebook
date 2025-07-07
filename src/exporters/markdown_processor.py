import markdown2

class MarkdownProcessor:
    def process_markdown(self, markdown_content):
        # Remove YAML front matter if present
        markdown_content = self.remove_yaml_frontmatter(markdown_content)
        
        # Adjust heading levels for proper hierarchy (shift all headings down by 3 levels)
        markdown_content = self.adjust_heading_levels(markdown_content)
        
        # Convert Markdown to HTML using markdown2
        html_content = markdown2.markdown(markdown_content, extras=['fenced-code-blocks', 'tables', 'header-ids'])
        return html_content
    
    def adjust_heading_levels(self, content):
        """
        Adjust heading levels to fit into the document hierarchy.
        
        Document hierarchy:
        H1: Book title (AI Engineer Guide)
        H2: Major section (CS 전공 지식)
        H3: Subsection (운영체제)
        H4: File content heading level 1 (# in markdown)
        H5: File content heading level 2 (## in markdown)
        H6: File content heading level 3 (### in markdown)
        
        Args:
            content: Markdown content
            
        Returns:
            Markdown content with adjusted heading levels
        """
        lines = content.split('\n')
        adjusted_lines = []
        
        for line in lines:
            # Check if line starts with heading markers
            if line.startswith('#'):
                # Count the number of # characters
                heading_level = 0
                for char in line:
                    if char == '#':
                        heading_level += 1
                    else:
                        break
                
                # Adjust heading level (add 3 to shift H1->H4, H2->H5, etc.)
                new_heading_level = min(heading_level + 3, 6)  # Max heading level is H6
                
                # Reconstruct the heading with new level
                heading_text = line[heading_level:].strip()
                adjusted_line = '#' * new_heading_level + ' ' + heading_text
                adjusted_lines.append(adjusted_line)
            else:
                adjusted_lines.append(line)
        
        return '\n'.join(adjusted_lines)
    
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
        # Check if content starts with YAML front matter delimiter
        if not content.strip().startswith('---'):
            return content
        
        # Find the end of the YAML front matter
        # Look for the closing --- on a line by itself
        lines = content.split('\n')
        end_index = None
        
        # Start from line 1 (skip the opening ---)
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if line == '---':
                end_index = i
                break
        
        # If we found the closing delimiter, remove the front matter
        if end_index is not None:
            # Keep everything after the closing --- line
            remaining_lines = lines[end_index + 1:]
            cleaned_content = '\n'.join(remaining_lines)
            # Remove any leading whitespace that might be left
            cleaned_content = cleaned_content.lstrip()
            return cleaned_content
        
        # If no closing delimiter found, return original content
        return content
