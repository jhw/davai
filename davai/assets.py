import os
import logging
from fuzzywuzzy import fuzz
from davai.code_block import CodeBlock

class Assets(list):
    """
    Custom class to manage a list of CodeBlock objects.
    """

    @property
    def paths(self):
        """Returns a list of paths from the CodeBlock head path attributes."""
        return [asset.head.path for asset in self]

    def match(self, text, threshold=0.7):
        """
        Matches assets based on fuzzy matching of the provided text input.
        Compares the full text against each asset path in the CodeBlock head objects.
        Returns an instance of Assets containing the matched assets.
        """
        matched_assets = Assets()

        # Preprocess the input text to make it lowercase
        processed_text = text.lower()

        # Iterate over each asset and calculate the fuzzy matching score
        for asset in self:
            # Get the base name of the asset (without the extension) and lowercase it
            asset_base = os.path.splitext(os.path.basename(asset.head.path))[0].lower()

            # Calculate the fuzzy matching score
            score = fuzz.partial_ratio(asset_base, processed_text)

            # Normalize the score to create a probability (score is between 0 and 100, so divide by 100)
            probability = score / 100.0

            # If the probability meets or exceeds the threshold, log it and add the asset to matched_assets
            if probability >= threshold:
                logging.info(f"Asset: {asset.head.path}, Score: {probability:.2f}")
                matched_assets.append(asset)

        return matched_assets
