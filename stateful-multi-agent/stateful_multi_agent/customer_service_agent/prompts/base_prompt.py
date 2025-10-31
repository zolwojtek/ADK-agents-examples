"""
Base prompt template for all agents.
"""

from typing import Dict, Any
from pathlib import Path
import yaml

class BasePrompt:
    """Base class for all prompts."""
    
    def __init__(self, template_path: str):
        """
        Initialize prompt with template.
        
        Args:
            template_path: Path to template file
        """
        self.template_path = Path(template_path)
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Load template from file."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        return self.template_path.read_text()
    
    def format(self, **kwargs: Any) -> str:
        """
        Format template with variables.
        
        Args:
            **kwargs: Variables to format template with
            
        Returns:
            str: Formatted template
        """
        return self.template.format(**kwargs)
    
    def validate(self) -> bool:
        """
        Validate template structure.
        
        Returns:
            bool: True if valid
        """
        required_sections = [
            "<objectives>",
            "<capabilities>",
            "<rules>",
            "<context>"
        ]
        
        return all(section in self.template for section in required_sections)

class YAMLPrompt(BasePrompt):
    """Prompt that loads from YAML file."""
    
    def _load_template(self) -> str:
        """Load and parse YAML template."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
            
        with open(self.template_path) as f:
            data = yaml.safe_load(f)
            
        return self._convert_to_string(data)
    
    def _convert_to_string(self, data: Dict[str, Any]) -> str:
        """Convert YAML data to prompt string."""
        sections = []
        
        # Add objectives
        if "objectives" in data:
            objectives = ["   <objective>{}</objective>".format(obj)
                        for obj in data["objectives"]]
            sections.append("   <objectives>\n{}\n   </objectives>".format(
                "\n".join(objectives)
            ))
        
        # Add capabilities
        if "capabilities" in data:
            capabilities = []
            for cap in data["capabilities"]:
                guidelines = ["            <guideline>{}</guideline>".format(g)
                            for g in cap["guidelines"]]
                capabilities.append(
                    "      <capability>\n"
                    "         <n>{}</n>\n"
                    "         <guidelines>\n{}\n"
                    "         </guidelines>\n"
                    "      </capability>".format(
                        cap["name"],
                        "\n".join(guidelines)
                    )
                )
            sections.append("   <capabilities>\n{}\n   </capabilities>".format(
                "\n".join(capabilities)
            ))
        
        # Add rules
        if "rules" in data:
            rules = []
            for category, rule_list in data["rules"].items():
                category_rules = ["         <rule>{}</rule>".format(rule)
                                for rule in rule_list]
                rules.append(
                    "      <{}>\n{}\n"
                    "      </{}>".format(
                        category,
                        "\n".join(category_rules),
                        category
                    )
                )
            sections.append("   <rules>\n{}\n   </rules>".format(
                "\n".join(rules)
            ))
        
        # Add context template
        if "context" in data:
            sections.append(data["context"])
        
        return "\n\n".join(sections)
