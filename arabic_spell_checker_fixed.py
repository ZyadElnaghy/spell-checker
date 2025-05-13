import tkinter as tk
from tkinter import scrolledtext
import re
import os
import Levenshtein

class ArabicSpellChecker:
    def __init__(self, word_list_path):
        """Initialize the spell checker with a word list."""
        self.word_list = self.load_word_list(word_list_path)
        
    def load_word_list(self, path):
        """Load Arabic words from a text file."""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return set([line.strip() for line in file if line.strip()])
        except FileNotFoundError:
            print(f"Error: Word list file not found at {path}")
            return set()
            
    def remove_diacritics(self, text):
        """Remove Arabic diacritics from text."""
        return re.sub(r'[\u064B-\u065F]', '', text)
        
    def normalize_text(self, text):
        """Normalize Arabic text by replacing certain characters."""
        text = text.replace('ى', 'ي')  # Replace Alif Maksura with Ya
        text = text.replace('ة', 'ه')  # Replace Ta Marbuta with Ha
        text = text.replace('أ', 'ا')  # Replace Hamza-Alif with Alif
        text = text.replace('إ', 'ا')  # Replace Hamza-Alif with Alif
        text = text.replace('آ', 'ا')  # Replace Madda-Alif with Alif
        return text
        
    def get_character_groups(self):
        """Get groups of similar Arabic characters that are commonly confused."""
        return [
            {'ا', 'أ', 'إ', 'آ'},  # Alif variations
            {'ي', 'ى'},           # Ya and Alif Maksura
            {'ه', 'ة'},           # Ha and Ta Marbuta
            {'و', 'ؤ'},           # Waw variations
            {'ك', 'گ'},           # Kaf variations
            {'ت', 'ط'},           # Ta-like sounds
            {'س', 'ص'},           # Seen-like sounds
            {'د', 'ض'},           # Dal-like sounds
            {'ح', 'ه', 'خ'},      # Throaty sounds
            {'ز', 'ذ', 'ظ'}       # Z-like sounds
        ]
        
    def calculate_phonetic_distance(self, char1, char2):
        """Calculate phonetic distance between two Arabic characters."""
        if char1 == char2:
            return 0
            
        char_groups = self.get_character_groups()
        
        # Check if both characters are in the same phonetic group
        for group in char_groups:
            if char1 in group and char2 in group:
                return 0.5  # Characters in same group are more similar
        
        return 1  # Default distance for unrelated characters
        
    def custom_distance(self, word1, word2):
        """Calculate a custom distance between two words considering Arabic phonetics."""
        # First use basic Levenshtein as a base
        base_distance = Levenshtein.distance(word1, word2)
        
        # Then apply phonetic adjustments
        phonetic_adjustment = 0
        min_len = min(len(word1), len(word2))
        
        for i in range(min_len):
            if word1[i] != word2[i]:
                phonetic_adjustment += self.calculate_phonetic_distance(word1[i], word2[i]) - 1
        
        # Adjust the base distance
        adjusted_distance = max(0, base_distance + phonetic_adjustment)
        return adjusted_distance
        
    def get_suggestions(self, word, max_suggestions=3):
        """Find suggested corrections for a word using enhanced distance metrics."""
        suggestions = []
        word_len = len(word)
        
        # Prefer words of similar length
        for dict_word in self.word_list:
            dict_word_len = len(dict_word)
            
            # Skip words with very different lengths
            if abs(word_len - dict_word_len) > min(3, word_len // 2 + 1):
                continue
                
            # Calculate custom distance that considers Arabic phonetics
            adjusted_distance = self.custom_distance(word, dict_word)
            
            # Apply length-based normalization
            max_len = max(word_len, dict_word_len)
            if max_len > 0:
                normalized_distance = adjusted_distance / max_len
            else:
                normalized_distance = adjusted_distance
            
            # Apply prefix and suffix matching bonuses (important for Arabic roots)
            prefix_length = 0
            for i in range(min(word_len, dict_word_len)):
                if word[i] == dict_word[i]:
                    prefix_length += 1
                else:
                    break
            
            suffix_length = 0
            for i in range(1, min(word_len, dict_word_len) + 1):
                if word_len >= i and dict_word_len >= i and word[-i] == dict_word[-i]:
                    suffix_length += 1
                else:
                    break
            
            # Root matching is particularly important in Arabic
            # More weight to prefix since Arabic words often share roots at the beginning
            prefix_bonus = prefix_length / max(word_len, 1) if prefix_length > 1 else 0
            suffix_bonus = suffix_length / max(word_len, 1) if suffix_length > 1 else 0
            
            # Length similarity (closer to 1 is better)
            length_ratio = min(word_len, dict_word_len) / max(word_len, dict_word_len) if max_len > 0 else 0
            
            # Calculate final weighted score
            weighted_score = (
                normalized_distance 
                - (prefix_bonus * 0.4)  # Prefix is important in Arabic
                - (suffix_bonus * 0.2)  # Suffix less important but still relevant
                - (length_ratio * 0.2)  # Length similarity
            )
            
            # Add contextual pattern matching for common Arabic patterns
            if prefix_length >= 3 and suffix_length >= 1:
                weighted_score -= 0.3  # Strong bonus for matching both prefix and suffix
            
            suggestions.append((dict_word, weighted_score))
        
        # Sort by weighted score (lower is better) and take top suggestions
        suggestions.sort(key=lambda x: x[1])
        return [word for word, _ in suggestions[:max_suggestions]]
        
    def check_text(self, text):
        """Check spelling in a text and return misspelled words with suggestions."""
        # Preprocess text
        text = self.remove_diacritics(text)
        text = self.normalize_text(text)
        
        # Split text into words
        words = text.split()
        
        # Check each word
        misspelled = {}
        for word in words:
            # Skip empty words or punctuation-only words
            if not word or not re.search(r'[\u0600-\u06FF]', word):
                continue
                
            # Remove punctuation
            clean_word = re.sub(r'[^\u0600-\u06FF]', '', word)
            
            if clean_word and clean_word not in self.word_list:
                suggestions = self.get_suggestions(clean_word)
                misspelled[word] = suggestions
                
        return misspelled

class SpellCheckerApp:
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Arabic Spell Checker")
        self.root.geometry("600x500")
        
        # Initialize spell checker
        current_dir = os.path.dirname(os.path.abspath(__file__))
        word_list_path = os.path.join(current_dir, "ar-words.txt")
        self.spell_checker = ArabicSpellChecker(word_list_path)
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        """Create and arrange the GUI widgets."""
        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, fill=tk.X, padx=10)
        
        tk.Label(input_frame, text="Enter Arabic text:").pack(anchor='w')
        
        # Text input
        self.text_input = scrolledtext.ScrolledText(input_frame, height=6, width=60, wrap=tk.WORD)
        self.text_input.pack(fill=tk.X, pady=5)
        self.text_input.configure(font=("Arial", 14))
        
        # Check button
        check_button = tk.Button(input_frame, text="Check Spelling", command=self.check_spelling)
        check_button.pack(pady=10)
        
        # Results frame
        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(result_frame, text="Results:").pack(anchor='w')
        
        # Results display
        self.result_display = scrolledtext.ScrolledText(result_frame, height=12, width=60, wrap=tk.WORD)
        self.result_display.pack(fill=tk.BOTH, expand=True, pady=5)
        self.result_display.configure(font=("Arial", 14), state='disabled')
        
    def check_spelling(self):
        """Handle the spell checking process when button is clicked."""
        # Get input text
        text = self.text_input.get('1.0', tk.END).strip()
        
        if not text:
            self.update_result("Please enter some text to check.")
            return
            
        # Check spelling
        misspelled = self.spell_checker.check_text(text)
        
        # Display results
        if not misspelled:
            result = "No spelling errors found!"
        else:
            result = f"Original text: {text}\n\nMisspelled words:\n"
            for word, suggestions in misspelled.items():
                result += f"\n• {word}:\n"
                if suggestions:
                    result += f"  Suggestions: {', '.join(suggestions)}"
                else:
                    result += "  No suggestions available."
                    
        self.update_result(result)
        
    def update_result(self, text):
        """Update the result display with new text."""
        self.result_display.configure(state='normal')
        self.result_display.delete('1.0', tk.END)
        self.result_display.insert('1.0', text)
        self.result_display.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = SpellCheckerApp(root)
    root.mainloop()
