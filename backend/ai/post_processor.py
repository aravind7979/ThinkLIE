import re

class PostProcessor:
    def __init__(self):
        pass

    def process(self, raw_response: str) -> str:
        """
        Formats output with standard markdown structured elements.
        Improves readability without altering meaning.
        """
        # Ensure that Step headers are bold if they aren't already
        processed = re.sub(r'(Step \d+:.*?)(?:\n|$)', r'**\1**\n', raw_response)
        
        # Clean up excessive newlines
        processed = re.sub(r'\n{3,}', '\n\n', processed)
        
        return processed.strip()

post_processor = PostProcessor()
