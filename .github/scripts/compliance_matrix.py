#!/usr/bin/env python3
"""
Generate spec-compliance-matrix.md from YAML files.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

class MarkdownGenerator:
    def __init__(self):
        self.template_data = None
        self.language_data = {}
        self.languages = []

    def load_yaml_files(self, yaml_dir: Path):
        """Load template.yaml and all language-specific YAML files."""
        template_file = yaml_dir / 'template.yaml'

        with open(template_file, 'r', encoding='utf-8') as f:
            self.template_data = yaml.safe_load(f)

        for lang_config in self.template_data['languages']:
            lang_name = lang_config['name']
            lang_file_path = yaml_dir / lang_config['location']

            if not lang_file_path.exists():
                raise FileNotFoundError(f"Language file {lang_file_path} not found for {lang_name}")

            with open(lang_file_path, 'r', encoding='utf-8') as f:
                self.language_data[lang_name] = yaml.safe_load(f)

        self.languages = [lang['name'] for lang in self.template_data['languages']]

    def update_markdown_content(self, md_file_path: Path) -> str:
        """Update the markdown content with new tables generated from YAML data."""
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for section in self.template_data['sections']:
            section_name = section['name']
            new_table = self._generate_table(section_name, section)
            content = self._replace_section_table(content, section_name, new_table)

        return content

    def _generate_table(self, section_name: str, section_data: Dict[str, Any]) -> str:
        """Generate markdown table for a section."""
        features = section_data['features']
        if not features:
            raise ValueError(f"Section '{section_name}' has no features defined")

        # Use section-specific languages if available, otherwise fall back to global
        languages = section_data.get('languages', self.languages)
        
        has_optional_column = not section_data.get('hide_optional_column', False)

        # Build header
        header_columns = ['Feature']
        if has_optional_column:
            header_columns.append('Optional')
        header_columns.extend(languages)

        rows = self._create_table_header(header_columns)

        # Process features
        for feature in features:
            if 'features' in feature:
                # Subsection header
                heading = feature['heading']
                cells = [heading]
                if has_optional_column:
                    cells.append('Optional')
                cells.extend(languages)
                rows.append(self._create_table_row(cells))
                
                for sub_feature in feature['features']:
                    rows.append(self._build_feature_row(sub_feature, languages, has_optional_column, section_name, heading))
            else:
                rows.append(self._build_feature_row(feature, languages, has_optional_column, section_name))

        return '\n'.join(rows)

    def _replace_section_table(self, content: str, section_name: str, new_table: str) -> str:
        """Replace the table in a specific section."""
        # Pattern to match a section header and its content until the next section or end
        section_pattern = rf'(## {re.escape(section_name)}.*?\n)(.*?)(?=\n## |\Z)'
        
        def replace_section(match):
            section_header = match.group(1)
            existing_content = match.group(2)

            # Pattern to match markdown tables (lines starting and ending with |)
            table_pattern = r'\|[^\n]+\|(?:\n\|[^\n]+\|)*'
            
            if re.search(table_pattern, existing_content):
                # Replace existing table
                new_content = re.sub(table_pattern, new_table, existing_content, count=1)
            else:
                # Add new table if none exists
                new_content = existing_content.rstrip() + '\n\n' + new_table + '\n'

            return section_header + new_content

        return re.sub(section_pattern, replace_section, content, flags=re.DOTALL)

    def _build_feature_row(self, feature: Dict, languages: List[str], has_optional_column: bool, section_name: str, heading_name: str = None) -> str:
        """Build a single feature row."""
        cells = [feature['name']]
        
        if has_optional_column:
            cells.append(self._get_optional_marker(feature))
        
        for lang in languages:
            cells.append(self._get_language_status(lang, section_name, feature['name'], heading_name))
        
        return self._create_table_row(cells)

    def _create_table_header(self, header_columns: List[str]) -> List[str]:
        """Create markdown table header with both header row and separator row."""
        header_row = self._create_table_row(header_columns)
        separators = ['-' * len(col) for col in header_columns] # Sized to match header column widths
        separator_row = self._create_table_row(separators)
        return [header_row, separator_row]

    def _create_table_row(self, cells: List[str]) -> str:
        """Create a markdown table row from cells."""
        joined_cells = ' | '.join(cells)
        return f"| {joined_cells} |"

    def _get_language_status(self, lang: str, section_name: str, feature_name: str, heading_name: str = None) -> str:
        """Get the status of a feature for a specific language."""
        lang_sections = self.language_data[lang]['sections']
        
        # Find the section with matching name
        lang_section = None
        for sect in lang_sections:
            if sect['name'] == section_name:
                lang_section = sect
                break
        
        if lang_section:
            status = self._find_feature_status(lang_section['features'], feature_name, heading_name)
            return status if status is not None else ''

        return ''

    def _find_feature_status(self, features: List[Dict], feature_name: str, heading_name: str = None) -> Optional[str]:
        """Search for a feature status in a flat or one-level hierarchical structure."""
        
        for feature in features:
            if feature.get('name') == feature_name:
                # Direct feature match (for top-level features or when no heading specified)
                if heading_name is None:
                    status = feature['status']
                    return self._convert_status_to_symbol(status)
            elif 'features' in feature and feature.get('heading'):
                # This is a heading with nested features
                if heading_name is None or feature.get('heading') == heading_name:
                    # Search within this heading if it matches or if no specific heading required
                    for nested_feature in feature['features']:
                        if nested_feature.get('name') == feature_name:
                            status = nested_feature['status']
                            return self._convert_status_to_symbol(status)
        
        # If we were looking for a specific heading but didn't find it, try without heading constraint
        if heading_name is not None:
            return self._find_feature_status(features, feature_name, None)
            
        return None  # Return None when not found

    def _get_optional_marker(self, feature_item: Dict) -> str:
        """Get the optional marker for a feature."""
        if feature_item.get('optional') is True:
            return 'X'
        elif feature_item.get('optional_one_of_group_is_required') is True:
            return '*'
        elif 'optional' in feature_item:
            return str(feature_item['optional'])
        return ''

    def _convert_status_to_symbol(self, status) -> str:
        """Convert status values to markdown symbols."""
        if status == '?':
            return ''
        else:
            return status

def main():
    """Main function to regenerate markdown from YAML files."""
    # Get the repository root (3 levels up from this script)
    repo_root = Path(__file__).parent.parent.parent
    yaml_dir = repo_root / 'spec-compliance-matrix'
    md_file = repo_root / 'spec-compliance-matrix.md'

    generator = MarkdownGenerator()
    generator.load_yaml_files(yaml_dir)
    
    # Generate the updated markdown content and write to file
    updated_content = generator.update_markdown_content(md_file)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

if __name__ == '__main__':
    main()
