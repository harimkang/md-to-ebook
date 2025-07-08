import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class MermaidRenderer:
    def __init__(self):
        self.playwright = None
        self.browser = None
        
    async def init_browser(self):
        """Initialize the browser for rendering"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
    
    async def close_browser(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def render_mermaid_to_svg(self, mermaid_code, theme='default'):
        """
        Render Mermaid diagram to SVG format
        
        Args:
            mermaid_code: The Mermaid diagram code
            theme: Theme for the diagram ('default', 'dark', 'forest', etc.)
            
        Returns:
            SVG string of the rendered diagram
        """
        await self.init_browser()
        
        # Create HTML content with Mermaid
        html_content = self._create_mermaid_html(mermaid_code, theme)
        
        page = await self.browser.new_page()
        
        try:
            # Set page content
            await page.set_content(html_content)
            
            # Wait for Mermaid to render
            await page.wait_for_selector('#mermaid-diagram', timeout=10000)
            await page.wait_for_timeout(1000)  # Additional wait for rendering to complete
            
            # Get the SVG content
            svg_content = await page.evaluate('''
                () => {
                    const svg = document.querySelector('#mermaid-diagram svg');
                    return svg ? svg.outerHTML : null;
                }
            ''')
            
            if svg_content:
                # Process SVG for better PDF rendering
                return self._process_svg_for_pdf(svg_content)
            else:
                raise Exception("Failed to render Mermaid diagram")
                
        finally:
            await page.close()
    
    def _create_mermaid_html(self, mermaid_code, theme='default'):
        """Create HTML content with Mermaid diagram"""
        # Configure Mermaid theme for better visibility on white background
        mermaid_config = {
            'theme': 'base',
            'themeVariables': {
                'primaryColor': '#2563eb',  # Blue
                'primaryTextColor': '#1f2937',  # Dark gray
                'primaryBorderColor': '#374151',  # Gray
                'lineColor': '#374151',  # Gray
                'secondaryColor': '#dbeafe',  # Light blue
                'tertiaryColor': '#f3f4f6',  # Light gray
                'background': '#ffffff',  # White
                'mainBkg': '#ffffff',  # White
                'secondBkg': '#f9fafb',  # Very light gray
                'tertiaryBkg': '#f3f4f6',  # Light gray
                'edgeLabelBackground': '#ffffff',
                'clusterBkg': '#f9fafb',
                'clusterBorder': '#d1d5db',
                'defaultLinkColor': '#374151',
                'titleColor': '#111827',
                'darkTextColor': '#111827',
                'textColor': '#111827',
                'labelTextColor': '#111827',
                'loopTextColor': '#111827',
                'noteTextColor': '#111827',
                'activationBorderColor': '#374151',
                'activationBkgColor': '#f3f4f6',
                'sequenceNumberColor': '#ffffff'
            }
        }
        
        config_json = json.dumps(mermaid_config)
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background: white;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                }}
                #mermaid-diagram {{
                    text-align: center;
                }}
                .mermaid {{
                    background: white;
                }}
                /* Ensure all text is dark and visible - more comprehensive */
                * {{
                    color: #111827 !important;
                }}
                .mermaid text, .mermaid tspan {{
                    fill: #111827 !important;
                    font-weight: 500;
                }}
                .mermaid .nodeLabel, .mermaid .edgeLabel {{
                    color: #111827 !important;
                }}
                .mermaid foreignObject div, .mermaid foreignObject span {{
                    color: #111827 !important;
                    font-weight: 500 !important;
                }}
                .mermaid .label {{
                    color: #111827 !important;
                }}
                .mermaid .cluster text {{
                    fill: #111827 !important;
                }}
                .mermaid .edgeLabel {{
                    color: #111827 !important;
                    background-color: white !important;
                }}
                .mermaid .node rect, .mermaid .node circle, .mermaid .node ellipse, .mermaid .node polygon {{
                    stroke: #374151 !important;
                    stroke-width: 2px !important;
                    fill: #f9fafb !important;
                }}
                .mermaid .edgePath path {{
                    stroke: #374151 !important;
                    stroke-width: 2px !important;
                }}
                .mermaid .arrowheadPath {{
                    fill: #374151 !important;
                    stroke: #374151 !important;
                }}
                /* Flowchart specific styles */
                .mermaid .flowchart-link {{
                    stroke: #374151 !important;
                    stroke-width: 2px !important;
                }}
                /* Class diagram specific styles */
                .mermaid .classGroup rect {{
                    stroke: #374151 !important;
                    stroke-width: 2px !important;
                    fill: #f9fafb !important;
                }}
                .mermaid .classGroup text {{
                    fill: #111827 !important;
                    font-weight: 500;
                }}
                .mermaid .relation {{
                    stroke: #374151 !important;
                    stroke-width: 2px !important;
                }}
                /* Force all text elements to be visible */
                div, span, p, text, tspan {{
                    color: #111827 !important;
                    fill: #111827 !important;
                    font-weight: 500 !important;
                }}
                /* Override any potential white text */
                [fill="white"], [fill="#ffffff"], [fill="#fff"] {{
                    fill: #111827 !important;
                }}
                [color="white"], [color="#ffffff"], [color="#fff"] {{
                    color: #111827 !important;
                }}
            </style>
        </head>
        <body>
            <div id="mermaid-diagram" class="mermaid">
                {mermaid_code}
            </div>
            <script>
                const config = {config_json};
                mermaid.initialize(config);
                mermaid.init();
            </script>
        </body>
        </html>
        '''
    
    def _process_svg_for_pdf(self, svg_content):
        """Process SVG to ensure good visibility in PDF"""
        soup = BeautifulSoup(svg_content, 'lxml')
        
        # Remove html and body wrappers if they exist
        svg = soup.find('svg')
        if not svg and soup.find('html'):
            # Extract SVG from HTML wrapper
            html_tag = soup.find('html')
            svg = html_tag.find('svg') if html_tag else None
        
        if svg:
            # Ensure background is white
            svg['style'] = 'background: white;'
            
            # Convert foreignObject elements to native SVG text elements
            # Mermaid uses foreignObject for text, which WeasyPrint doesn't handle well
            converted_count = 0
            foreign_objects = soup.find_all('foreignobject')
            
            # Group foreignObjects by their parent class (for class diagrams)
            class_groups = {}
            
            # Check if this is a class diagram by looking at SVG role
            svg_element = soup.find('svg')
            is_class_diagram = False
            if svg_element and svg_element.get('aria-roledescription') == 'classDiagram':
                is_class_diagram = True
            
            for foreign_obj in foreign_objects:
                # Find the node parent (g.node.default for class diagrams)
                parent = foreign_obj.parent
                node_parent = None
                while parent and parent.name != 'svg':
                    parent_class = parent.get('class', '')
                    if isinstance(parent_class, list):
                        parent_class = ' '.join(parent_class)
                    
                    if 'node' in str(parent_class) and 'default' in str(parent_class):
                        node_parent = parent
                        break
                    parent = parent.parent
                
                # For class diagrams, group by the node parent
                if is_class_diagram and node_parent:
                    group_id = node_parent.get('data-id', 'class_unknown')
                    if group_id not in class_groups:
                        class_groups[group_id] = []
                    class_groups[group_id].append(foreign_obj)
                else:
                    # For other diagrams, treat individually
                    individual_key = f"individual_{len(class_groups)}"
                    class_groups[individual_key] = [foreign_obj]
            
            for group_id, group_objects in class_groups.items():
                # For class diagrams with multiple texts in same node, arrange vertically
                if is_class_diagram and len(group_objects) > 1:
                    for i, foreign_obj in enumerate(group_objects):
                        text_element = self._convert_foreign_object_to_text_for_class(foreign_obj, soup, i, len(group_objects))
                        if text_element:
                            foreign_obj.replace_with(text_element)
                            converted_count += 1
                        else:
                            foreign_obj.decompose()
                else:
                    # Single elements (flowcharts, etc.)
                    for foreign_obj in group_objects:
                        text_element = self._convert_foreign_object_to_text_simple(foreign_obj, soup)
                        if text_element:
                            foreign_obj.replace_with(text_element)
                            converted_count += 1
                        else:
                            foreign_obj.decompose()
            
            # Second pass: Process all remaining text elements
            for text in soup.find_all(['text', 'tspan']):
                self._apply_dark_text_style(text)
            
            # Third pass: Process path elements (lines, arrows, shapes)
            for path in soup.find_all('path'):
                self._apply_dark_stroke_style(path)
            
            # Fourth pass: Process shape elements (rectangles, circles, etc.)
            for shape in soup.find_all(['rect', 'circle', 'ellipse', 'polygon', 'polyline']):
                self._apply_shape_style(shape)
            
            # Fifth pass: Process g (group) elements that might contain text
            for group in soup.find_all('g'):
                self._process_group_elements(group)
            
            # Final pass: Ensure all text is visible with additional fallback styling
            self._apply_final_text_visibility_fixes(soup)
        
        # Return only the SVG part, not the HTML wrapper
        if svg:
            return str(svg)
        else:
            return str(soup)
    
    def _apply_final_text_visibility_fixes(self, soup):
        """Apply final fixes to ensure all text is visible"""
        # Find all text elements and ensure they have proper styling
        all_text_elements = soup.find_all(['text', 'tspan'])
        for text_elem in all_text_elements:
            # Make sure fill is always set to dark color
            text_elem['fill'] = '#111827'
            
            # Ensure style includes visible properties
            current_style = text_elem.get('style', '')
            if 'fill:' not in current_style:
                current_style += '; fill: #111827 !important'
            if 'font-weight:' not in current_style:
                current_style += '; font-weight: 500'
            if 'font-family:' not in current_style:
                current_style += '; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
            
            text_elem['style'] = current_style
        
        # Also check for any remaining foreign objects that might have been missed
        remaining_foreign = soup.find_all('foreignobject')
        for foreign_obj in remaining_foreign:
            # Force visibility on any remaining foreign objects
            for element in foreign_obj.find_all(['div', 'span', 'p']):
                element['style'] = element.get('style', '') + '; color: #111827 !important; font-weight: 500 !important;'
    
    def _convert_foreign_object_to_text_for_class(self, foreign_obj, soup, index, total_count):
        """Convert foreignObject to text element for class diagrams with proper vertical positioning"""
        try:
            # Extract text content
            text_content = ""
            text_divs = foreign_obj.find_all(['div', 'span'])
            for div in text_divs:
                content = div.get_text(strip=True)
                if content and len(content) > len(text_content):
                    text_content = content
            
            if not text_content:
                text_content = foreign_obj.get_text(strip=True)
            
            if not text_content:
                return None
            
            # Get dimensions
            width = float(foreign_obj.get('width', '100'))
            
            # Create text element with vertical positioning for class diagrams
            text_elem = soup.new_tag('text')
            
            # Position text elements vertically within the class box
            # Class boxes typically have sections: title, attributes, methods
            # We need to position texts within the visible area of the box
            
            # Calculate proper y position based on index
            # Start from a positive offset and space elements downward
            base_y = 15  # Start inside the box
            line_height = 16  # Space between lines
            y_offset = base_y + (index * line_height)
            
            # Skip empty content (first element is often empty)
            if not text_content.strip():
                return None
            
            text_elem['x'] = str(width / 2)
            text_elem['y'] = str(y_offset)
            text_elem['text-anchor'] = 'middle'
            text_elem['dominant-baseline'] = 'middle'
            text_elem['fill'] = '#111827'
            
            # Different styling for class name vs attributes/methods
            # First non-empty element is usually the class name
            if index <= 1 and not any(c in text_content for c in ['+', '-', '#', '~']):
                # Class name - bold and slightly larger
                text_elem['style'] = 'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif; font-size: 16px; font-weight: bold; fill: #111827;'
            else:
                # Attributes and methods - regular
                text_elem['style'] = 'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif; font-size: 14px; font-weight: 500; fill: #111827;'
            
            text_elem.string = text_content
            return text_elem
            
        except Exception as e:
            print(f"Warning: Failed to convert class foreignObject: {e}")
            return None

    def _convert_foreign_object_to_text_simple(self, foreign_obj, soup):
        """Simple conversion of foreignObject to SVG text element"""
        try:
            # Extract text content - get the most relevant text
            text_content = ""
            
            # Look for text in nested elements
            text_divs = foreign_obj.find_all(['div', 'span'])
            for div in text_divs:
                content = div.get_text(strip=True)
                if content and len(content) > len(text_content):
                    text_content = content
            
            # Fallback to all text
            if not text_content:
                text_content = foreign_obj.get_text(strip=True)
            
            if not text_content:
                return None
            
            # Get position from foreignObject attributes
            x_attr = foreign_obj.get('x', '0')
            y_attr = foreign_obj.get('y', '0')
            width = float(foreign_obj.get('width', '100'))
            height = float(foreign_obj.get('height', '20'))
            
            # Parse x and y coordinates
            try:
                x_pos = float(x_attr)
                y_pos = float(y_attr)
                
                # For class diagrams, use absolute positioning from foreignObject
                # For other diagrams, use relative positioning
                parent_class = self._get_parent_class_name(foreign_obj)
                if 'classGroup' in parent_class:
                    # Class diagram: use absolute positioning with small adjustments
                    text_elem = soup.new_tag('text')
                    text_elem['x'] = str(x_pos + width / 2)  # Center horizontally
                    text_elem['y'] = str(y_pos + height / 2 + 4)  # Center vertically with adjustment
                else:
                    # Other diagrams: use relative positioning
                    text_elem = soup.new_tag('text')
                    text_elem['x'] = str(width / 2)
                    text_elem['y'] = str(height / 2 + 4)
                    
            except (ValueError, TypeError):
                # Fallback to relative positioning
                text_elem = soup.new_tag('text')
                text_elem['x'] = str(width / 2)
                text_elem['y'] = str(height / 2 + 4)
            
            text_elem['text-anchor'] = 'middle'
            text_elem['dominant-baseline'] = 'middle'
            text_elem['fill'] = '#111827'
            text_elem['style'] = 'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif; font-size: 14px; font-weight: 500; fill: #111827;'
            text_elem.string = text_content
            
            return text_elem
            
        except Exception as e:
            print(f"Warning: Failed to convert foreignObject: {e}")
            return None
    
    def _get_parent_class_name(self, element):
        """Get class names from parent elements to determine diagram type"""
        parent = element.parent
        class_names = []
        
        while parent and parent.name != 'svg':
            if parent.get('class'):
                class_attr = parent.get('class')
                if isinstance(class_attr, list):
                    class_names.extend(class_attr)
                else:
                    class_names.append(class_attr)
            parent = parent.parent
        
        return ' '.join(class_names)

    def _convert_foreign_object_to_text(self, foreign_obj, soup):
        """Convert foreignObject with HTML content to native SVG text element"""
        try:
            # Extract all text content from the foreignObject
            text_elements = []
            all_text_nodes = foreign_obj.find_all(['div', 'span', 'p'])
            
            for element in all_text_nodes:
                text_content = element.get_text(strip=True) if element else ""
                if text_content:
                    text_elements.append(text_content)
            
            # If no individual elements found, try to get all text
            if not text_elements:
                text_content = foreign_obj.get_text(strip=True)
                if text_content:
                    text_elements = [text_content]
            
            if not text_elements:
                return None
            
            # Get position and size information from the foreignObject
            x = float(foreign_obj.get('x', '0'))
            y = float(foreign_obj.get('y', '0'))
            width = float(foreign_obj.get('width', '100'))
            height = float(foreign_obj.get('height', '18'))
            
            # Check if this foreignObject is within a transformed group
            parent_transform = self._get_parent_transform(foreign_obj)
            if parent_transform:
                x += parent_transform.get('x', 0)
                y += parent_transform.get('y', 0)
            
            # Create a group to hold multiple text elements if needed
            if len(text_elements) == 1:
                # Single text element
                text_elem = soup.new_tag('text')
                text_elem['x'] = str(x + width / 2)
                text_elem['y'] = str(y + height / 2 + 5)  # Slight vertical adjustment for better centering
                text_elem['text-anchor'] = 'middle'
                text_elem['dominant-baseline'] = 'middle'
                text_elem['fill'] = '#111827'
                text_elem['style'] = 'font-weight: 500; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif; font-size: 14px;'
                text_elem.string = text_elements[0]
                return text_elem
            else:
                # Multiple text elements (e.g., class diagram with title, attributes, methods)
                group = soup.new_tag('g')
                group['class'] = 'converted-text-group'
                
                line_height = 16
                start_y = y + 12  # Start with some padding from top
                
                for i, text_content in enumerate(text_elements):
                    text_elem = soup.new_tag('text')
                    text_elem['x'] = str(x + width / 2)
                    text_elem['y'] = str(start_y + (i * line_height))
                    text_elem['text-anchor'] = 'middle'
                    text_elem['dominant-baseline'] = 'middle'
                    text_elem['fill'] = '#111827'
                    
                    # Apply different styling based on position (first element might be title)
                    if i == 0 and len(text_elements) > 1:
                        # Title styling
                        text_elem['style'] = 'font-weight: bold; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif; font-size: 14px;'
                    else:
                        # Regular styling
                        text_elem['style'] = 'font-weight: 500; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif; font-size: 12px;'
                    
                    text_elem.string = text_content
                    group.append(text_elem)
                
                return group
            
        except Exception as e:
            print(f"Warning: Failed to convert foreignObject to text: {e}")
            return None
    
    def _get_parent_transform(self, element):
        """Extract transform information from parent elements"""
        parent = element.parent
        transform_info = {'x': 0, 'y': 0}
        
        while parent and parent.name != 'svg':
            if parent.name == 'g' and parent.get('transform'):
                transform = parent.get('transform')
                # Simple parsing for translate(x,y) transforms
                if 'translate(' in transform:
                    # Extract translate values
                    import re
                    match = re.search(r'translate\(([^,\)]+)(?:,([^,\)]+))?\)', transform)
                    if match:
                        x_val = float(match.group(1))
                        y_val = float(match.group(2)) if match.group(2) else 0
                        transform_info['x'] += x_val
                        transform_info['y'] += y_val
            parent = parent.parent
        
        return transform_info
    
    def _apply_dark_text_style(self, text_element):
        """Apply dark styling to text elements"""
        current_style = text_element.get('style', '')
        style_parts = []
        if current_style:
            style_parts = [part.strip() for part in current_style.split(';') 
                         if part.strip() and not part.strip().startswith('fill:')]
        
        style_parts.extend([
            'fill: #111827 !important',
            'font-weight: 500',
            'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
        ])
        
        text_element['style'] = '; '.join(style_parts)
        text_element['fill'] = '#111827'
    
    def _apply_dark_stroke_style(self, path_element):
        """Apply dark stroke styling to path elements"""
        current_style = path_element.get('style', '')
        style_parts = []
        if current_style:
            style_parts = [part.strip() for part in current_style.split(';') 
                         if part.strip()]
        
        # Ensure dark stroke for visibility
        has_stroke = any('stroke:' in part for part in style_parts)
        if not has_stroke:
            style_parts.append('stroke: #374151')
            style_parts.append('stroke-width: 2px')
        else:
            # Update existing stroke to be darker
            style_parts = [part if not part.strip().startswith('stroke:') 
                         else 'stroke: #374151' for part in style_parts]
        
        path_element['style'] = '; '.join(style_parts)
    
    def _apply_shape_style(self, shape_element):
        """Apply styling to shape elements"""
        current_style = shape_element.get('style', '')
        style_parts = []
        if current_style:
            style_parts = [part.strip() for part in current_style.split(';') 
                         if part.strip()]
        
        # Ensure dark stroke and light fill for shapes
        has_stroke = any('stroke:' in part for part in style_parts)
        has_fill = any('fill:' in part for part in style_parts)
        
        if not has_stroke:
            style_parts.append('stroke: #374151')
            style_parts.append('stroke-width: 2px')
        
        if not has_fill:
            style_parts.append('fill: #f9fafb')
        
        shape_element['style'] = '; '.join(style_parts)
    
    def _process_group_elements(self, group):
        """Process group elements that might contain text"""
        current_class = group.get('class', '')
        if isinstance(current_class, list):
            current_class = ' '.join(current_class)
        
        if 'label' in current_class.lower() or 'text' in current_class.lower():
            # Find all text elements within this group
            for text in group.find_all(['text', 'tspan']):
                self._apply_dark_text_style(text)
            
            # Also check for foreignObject elements
            for foreign_obj in group.find_all('foreignobject'):
                for element in foreign_obj.find_all(['div', 'span']):
                    element['style'] = element.get('style', '') + '; color: #111827 !important;'
    
    def render_mermaid_sync(self, mermaid_code, theme='default'):
        """
        Synchronous wrapper for rendering Mermaid diagrams
        
        Args:
            mermaid_code: The Mermaid diagram code
            theme: Theme for the diagram
            
        Returns:
            SVG string of the rendered diagram
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(self.render_mermaid_to_svg(mermaid_code, theme))
        finally:
            # Don't close the loop here as it might be used elsewhere
            pass
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.browser:
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.close_browser())
            except Exception:
                pass
