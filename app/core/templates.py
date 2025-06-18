import json
from typing import List, Dict, Tuple

class TemplateManager:
    """
    TemplateManager is a utility class designed to help construct and parse prompts for question-answering systems
    that rely on provided text excerpts. It standardizes the format of prompts and responses to ensure consistency
    and facilitate downstream processing.
    Description:
        - The class initializes with a template string that instructs the user to cite sources using links only,
          and to answer questions based solely on provided excerpts.
        - It provides a method to build a prompt by formatting a list of excerpts (each with associated metadata)
          and an augmented query into a single string.
        - It also provides a method to parse a JSON-formatted response string into a Python dictionary, raising
          an error if the response cannot be parsed.
    Features:
        - Standardizes prompt construction for QA systems using context excerpts.
        - Associates each excerpt with its source and chunk identifier for traceability.
        - Parses model responses from JSON format, with error handling for invalid responses.
    Usage:
        1. Instantiate the TemplateManager.
        2. Use `build_prompt()` to create a prompt string from a list of excerpts and a query.
        3. Use `parse_response()` to convert a JSON response string into a Python dictionary.
    Conclusion:
        TemplateManager simplifies the process of preparing prompts and handling responses for systems that
        answer questions based on specific text excerpts, ensuring clarity, consistency, and ease of integration.
    """
    def __init__(self):
        self.template = (
            "Always cite sources in links only.\n\n"
            "Answer based solely on the following excerpts:\n\n"
        )

    def build_prompt(self, excerpts: List[Tuple[str, Dict]], augmented_query: str) -> str:
        prompt = self.template
        for i, (text, meta) in enumerate(excerpts, start=1):
            prompt += f"Excerpt [{i}] (source: {meta['source']} | chunk_id: {meta.get('chunk_id')}):\n{text}\n\n"
        return prompt + f"QUESTION: {augmented_query}\nANSWER:"

    def parse_response(self, response: str) -> Dict:
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            raise ValueError("Unable to parse the response: the provided string is not valid JSON.\nPlease ensure the response format adheres to the expected specification.")