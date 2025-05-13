# Arabic Spell Checker

A simple Arabic spell checker with a GUI built using Python and tkinter.

## Features

- GUI interface with tkinter
- Loads Arabic words from a dictionary file
- Removes Arabic diacritics
- Normalizes Arabic characters (ى → ي, ة → ه, أ/إ/آ → ا)
- Suggests corrections for misspelled words using enhanced Levenshtein distance with Arabic-specific optimizations

## Requirements

- Python 3.x
- tkinter (usually comes with Python)
- python-Levenshtein

## Installation

1. Install required packages:
   ```
   pip install python-Levenshtein
   ```

2. Make sure `ar-words.txt` is in the same directory as the script.

## Usage

1. Run the script:
   ```
   python arabic_spell_checker.py
   ```

2. Enter Arabic text in the input box.
3. Click "Check Spelling" to see results.
4. Misspelled words will be displayed along with suggested corrections.

## How It Works

1. The program loads a list of Arabic words from `ar-words.txt`.
2. When you enter text and click the button:
   - It removes diacritics and normalizes characters
   - It splits the text into words
   - For each word not in the dictionary, it uses an enhanced algorithm to suggest similar words

## Advanced Features

The spell checker uses several techniques to improve suggestion quality:

1. **Phonetic Character Grouping**: Similar-sounding Arabic characters are grouped together
2. **Arabic-Specific Character Normalization**: Handles various forms of the same letter
3. **Root-Based Matching**: Gives higher weight to words with matching prefixes (important in Arabic morphology)
4. **Custom Distance Calculation**: Enhances standard Levenshtein distance with Arabic-specific adjustments
5. **Weighted Scoring System**: Considers prefix/suffix matching, length similarity, and phonetic patterns

## Extending the Dictionary

To add more words to the dictionary, simply add them to the `ar-words.txt` file, one word per line.
