"""Account name normalization utilities."""

from typing import Dict, List, Optional
from fuzzywuzzy import fuzz
import re


class AccountNormalizer:
    """Normalize and match account names."""

    def __init__(self, patterns: List[List[str]] = None, fuzzy_threshold: int = 85):
        """
        Initialize normalizer with known patterns and fuzzy threshold.

        Args:
            patterns: List of lists containing known account name variations
            fuzzy_threshold: Minimum Levenshtein ratio for fuzzy matching (0-100)
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.patterns = patterns or []
        self._pattern_map = self._build_pattern_map()

    def _build_pattern_map(self) -> Dict[str, str]:
        """Build a mapping of variations to canonical names."""
        pattern_map = {}
        for pattern_group in self.patterns:
            if pattern_group:
                canonical = pattern_group[0]  # First one is canonical
                for variation in pattern_group:
                    normalized = self._clean_name(variation)
                    pattern_map[normalized] = self._clean_name(canonical)
        return pattern_map

    def _clean_name(self, name: str) -> str:
        """Clean and standardize account name."""
        if not name:
            return ""

        # Convert to lowercase
        name = str(name).lower().strip()

        # Remove common suffixes and punctuation
        name = re.sub(r'\b(inc|incorporated|corp|corporation|llc|ltd|limited|co)\b\.?', '', name)
        name = re.sub(r'[^\w\s]', '', name)  # Remove punctuation
        name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace

        return name

    def normalize(self, account_name: str) -> str:
        """
        Normalize account name to canonical form.

        Args:
            account_name: Raw account name

        Returns:
            Normalized canonical account name
        """
        if not account_name:
            return ""

        cleaned = self._clean_name(account_name)

        # Check exact match in patterns
        if cleaned in self._pattern_map:
            return self._pattern_map[cleaned]

        # Check fuzzy match against known patterns
        best_match = None
        best_score = 0

        for pattern, canonical in self._pattern_map.items():
            score = fuzz.ratio(cleaned, pattern)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = canonical

        return best_match if best_match else cleaned

    def are_same_account(self, name1: str, name2: str) -> bool:
        """
        Check if two account names refer to the same account.

        Args:
            name1: First account name
            name2: Second account name

        Returns:
            True if names match after normalization
        """
        return self.normalize(name1) == self.normalize(name2)

    def find_canonical(self, account_name: str, existing_accounts: List[str]) -> Optional[str]:
        """
        Find canonical account name from list of existing accounts.

        Args:
            account_name: Account name to match
            existing_accounts: List of existing account names to match against

        Returns:
            Best matching existing account name or None
        """
        normalized_input = self.normalize(account_name)

        # Check exact normalized match
        for existing in existing_accounts:
            if self.normalize(existing) == normalized_input:
                return existing

        # Fuzzy match against original names
        best_match = None
        best_score = 0

        for existing in existing_accounts:
            score = fuzz.ratio(account_name.lower(), existing.lower())
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = existing

        return best_match
