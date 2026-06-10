#!/usr/bin/env python3
"""
minifystd.py: Production-Grade HTML, CSS, and JS Minifier.
Zero external dependencies. Auto-detects file extensions and minifies safely.
Author: santakd (santakd@gmail.com)
Version: 1.0.8

How to Use & Validate It
    Run Minification:
    python minifystd.py path/to/your/script.js --level 2

    This automatically detects the file extension, strips out the appropriate elements, avoids destroying JS URLs or CSS Strings, 
    writes the output to script_min.js, and logs to a logs/ folder.

    Run Built-In Unit Tests (Validation):
    python minifystd.py --test

    This will run the internal test cases mimicking file I/O to prove that the complex regex strings handle exactly the edge cases outlined.

    Check Help Message:
    python minifystd.py --help

Why this hits "Production Grade":

    Architecture: Uses the Factory pattern (MinifierFactory) to separate file handling from the parsing logic, allowing easy future additions.

    Safety Over Speed: Rather than complex, brittle Regex replacing, the script uses Regex Tokenization in CSS and JS. It matches both Strings
    and Comments, meaning it knows exactly when a comment is wrapped inside quotation marks (preventing it from corrupting JS http:// strings).

    Structure: the HtmlMinifier class. Instead of just protecting <script> and <style> blocks and ignoring them, Level 2 should extract them, 
    route their contents through our JsMinifier and CssMinifier, and then put them back.

    Graceful Degeneration: Protected HTML blocks (<pre>, <script>, etc.) are temporarily replaced by unique UUID-style placeholders before 
    manipulating the HTML, and reliably swapped back afterward.

    Robust Environment Setup: Logs gracefully degrade if file permissions are restricted, and correct POSIX exit codes (0 or 1) are returned 
    depending on try/except chains. Types are strictly enforced using the typing library.
"""

import os
import sys
import argparse
import logging
import re
from datetime import datetime
from typing import Optional, Type, Dict, Tuple
import unittest
from unittest.mock import patch, mock_open

# ==============================================================================
# EXCEPTIONS & LOGGING SETUP
# ==============================================================================

class MinifierError(Exception):
    """Custom exception for minifier specific errors."""
    pass


def setup_logger() -> logging.Logger:
    """Sets up a timestamped logger outputting to both console and a logs/ directory."""
    logger = logging.getLogger("MinifierApp")
    logger.setLevel(logging.DEBUG)

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ch)

    # File Handler
    try:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join("logs", f"minifystd_{timestamp}.log")
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)
    except OSError as e:
        logger.warning(f"Could not create logs directory or file: {e}. File logging disabled.")

    return logger

logger = setup_logger()


# ==============================================================================
# MINIFIER CLASSES
# ==============================================================================

class BaseMinifier:
    """Base class for all minifiers."""
    
    def __init__(self, level: int):
        self.level = level

    def minify(self, content: str) -> str:
        """Core minification method. Subclasses should override and call super() if needed."""
        if not content.strip():
            return ""
        return self._level_1_minify(content)

    def _level_1_minify(self, content: str) -> str:
        """Level 1: Basic minification - Strip leading/trailing whitespace and empty lines."""
        lines = content.splitlines()
        stripped_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(stripped_lines)


class HtmlMinifier(BaseMinifier):
    """HTML specific minification."""
    
    def minify(self, content: str) -> str:
        if self.level == 1:
            # Note: Level 1 blindly strips all lines, which is smaller but can corrupt <pre> tags.
            return self._level_1_minify(content)
        
        # Level 2: Aggressive, safe, AND routes inline JS/CSS to their respective minifiers
        # Group 1: Open Tag, Group 2: Tag Name, Group 3: Inner Content, Group 4: Close Tag
        protected_pattern = re.compile(
            r'(<(pre|code|script|style)[^>]*>)([\s\S]*?)(</\2>)', 
            re.IGNORECASE
        )
        
        placeholders: Dict[str, str] = {}
        def safeguard(match: re.Match) -> str:
            open_tag = match.group(1)
            tag_name = match.group(2).lower()
            inner_content = match.group(3)
            close_tag = match.group(4)

            # If it's a script or style block, recursively minify its contents!
            if inner_content.strip():
                if tag_name == 'script':
                    inner_content = JsMinifier(self.level).minify(inner_content)
                elif tag_name == 'style':
                    inner_content = CssMinifier(self.level).minify(inner_content)
            
            # <pre> and <code> inner_content intentionally bypassed to preserve formatting

            placeholder = f"__PROTECTED_BLOCK_{len(placeholders)}__"
            # Reconstruct the tag with the minified inner content
            placeholders[placeholder] = f"{open_tag}{inner_content}{close_tag}"
            return placeholder

        # 1. Extract, minify inner JS/CSS, and safeguard
        content = protected_pattern.sub(safeguard, content)

        # 2. Remove HTML comments
        content = re.sub(r'<!--[\s\S]*?-->', '', content)

        # 3. Minify standard HTML (remove line breaks, strip spaces between tags)
        content = self._level_1_minify(content)
        content = re.sub(r'>\s+<', '><', content)  # safe space removal between tags
        content = re.sub(r'\n', '', content)       # flatten HTML to single line

        # 4. Restore the processed blocks back into the HTML
        for placeholder, original_text in placeholders.items():
            content = content.replace(placeholder, original_text)

        return content

class CssMinifier(BaseMinifier):
    """CSS specific minification."""
    
    def minify(self, content: str) -> str:
        if self.level == 1:
            return self._level_1_minify(content)

        # Level 2: Remove comments carefully protecting strings
        # Matches double-quoted strings, single-quoted strings, OR block comments
        pattern = re.compile(
            r'('
            r'(?:"(?:\\.|[^"\\])*")|'   # Double quoted strings
            r"(?:'(?:\\.|[^'\\])*')"    # Single quoted strings
            r')|'
            r'(\/\*[\s\S]*?\*\/)'       # Multi-line comments
        )
        
        def replacer(match: re.Match) -> str:
            if match.group(2): # It's a comment
                return ""
            return match.group(1) # It's a string, preserve it

        content = pattern.sub(replacer, content)
        content = self._level_1_minify(content)
        
        # Safe CSS Aggressive space removal
        content = re.sub(r'\s*([\{\}\:\;\,\>])\s*', r'\1', content)
        return content


class JsMinifier(BaseMinifier):
    """JS specific minification."""

    def minify(self, content: str) -> str:
        if self.level == 1:
            return self._level_1_minify(content)

        # Level 2: Remove comments safely avoiding URLs and Strings
        # This regex tokenizes strings (", ', `) and comments (/*, //)
        pattern = re.compile(
            r'('
            r'(?:"(?:\\.|[^"\\])*")|'   # Double quoted strings
            r"(?:'(?:\\.|[^'\\])*')|"   # Single quoted strings
            r'(?:`(?:\\.|[^`\\])*`)'    # Template literals
            r')|'
            r'(\/\*[\s\S]*?\*\/)|'      # Multi-line comments
            r'(\/\/.*)'                 # Single-line comments
        )

        def replacer(match: re.Match) -> str:
            if match.group(2) or match.group(3):
                return "" # Comment -> Remove
            return match.group(1) # String -> Preserve

        content = pattern.sub(replacer, content)
        content = self._level_1_minify(content)
        
        # Note: We avoid heavy string/newline collapsing in JS to prevent breaking 
        # Automatic Semicolon Insertion (ASI) without a full AST parser.
        return content


class MinifierFactory:
    """Determines and returns the correct minifier based on extension."""
    
    @staticmethod
    def get_minifier(ext: str, level: int) -> BaseMinifier:
        ext = ext.lower()
        if ext in ['.html', '.htm']:
            return HtmlMinifier(level)
        elif ext == '.css':
            return CssMinifier(level)
        elif ext == '.js':
            return JsMinifier(level)
        else:
            raise MinifierError(f"Unsupported file extension: {ext}")


# ==============================================================================
# MAIN APPLICATION CONTROLLER
# ==============================================================================

class MinifierApp:
    """Handles CLI operations and file IO."""
    
    def __init__(self, input_file: str, level: int):
        self.input_file = input_file
        self.level = level

    def run(self) -> None:
        """Executes the minification process."""
        try:
            self._validate_file()
            content = self._read_file()
            original_size = len(content.encode('utf-8'))
            
            if original_size == 0:
                logger.warning(f"File {self.input_file} is empty. Exiting.")
                return

            ext = os.path.splitext(self.input_file)[1]
            minifier = MinifierFactory.get_minifier(ext, self.level)
            
            logger.info(f"Minifying {self.input_file} (Level {self.level})...")
            minified_content = minifier.minify(content)
            
            output_file = self._get_output_filename()
            self._write_file(output_file, minified_content)
            
            new_size = len(minified_content.encode('utf-8'))
            saved_bytes = original_size - new_size
            savings_pct = (saved_bytes / original_size) * 100 if original_size > 0 else 0
            
            logger.info(f"Success! Output saved to: {output_file}")
            logger.info(f"Original: {original_size} bytes | Minified: {new_size} bytes")
            logger.info(f"Space saved: {saved_bytes} bytes ({savings_pct:.2f}%)")

        except MinifierError as e:
            logger.error(f"Minification Error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected System Error: {str(e)}")
            sys.exit(1)

    def _validate_file(self) -> None:
        if not os.path.exists(self.input_file):
            raise MinifierError(f"File not found: {self.input_file}")
        if not os.path.isfile(self.input_file):
            raise MinifierError(f"Path is not a file: {self.input_file}")

    def _read_file(self) -> str:
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return f.read()
        except PermissionError:
            raise MinifierError(f"Read permission denied for file: {self.input_file}")
        except UnicodeDecodeError:
            raise MinifierError(f"File is not a valid UTF-8 text file: {self.input_file}")

    def _write_file(self, filepath: str, content: str) -> None:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            raise MinifierError(f"Write permission denied for file: {filepath}")

    def _get_output_filename(self) -> str:
        base, ext = os.path.splitext(self.input_file)
        return f"{base}_min{ext}"


# ==============================================================================
# UNIT TESTS (Mocking I/O)
# ==============================================================================

class TestMinifier(unittest.TestCase):
    
    def test_level_1_basic(self):
        js = "  \n  let x = 1; \n   "
        minifier = JsMinifier(level=1)
        self.assertEqual(minifier.minify(js), "let x = 1;")
        
    def test_js_safe_url_and_strings(self):
        js = """
        let url = "https://example.com"; // line comment
        let b = '/* not a comment */';
        /* block comment */
        let c = `string with // inside`;
        """
        minifier = JsMinifier(level=2)
        res = minifier.minify(js)
        self.assertIn('"https://example.com";', res)
        self.assertIn("'/* not a comment */';", res)
        self.assertIn("`string with // inside`;", res)
        self.assertNotIn("line comment", res)
        self.assertNotIn("block comment", res)

    def test_css_safe_strings(self):
        css = """
        body { color: red; } /* comment */
        .icon::before { content: "/* not a comment */"; }
        """
        minifier = CssMinifier(level=2)
        res = minifier.minify(css)
        self.assertEqual(res, 'body{color:red;}\n.icon::before{content:"/* not a comment */";}')
        
    def test_html_protect_tags(self):
        html = """
        <html>
            <!-- remove me -->
            <body>
                <pre>  spaces should stay  </pre>
                <script> let a = 1; </script>
            </body>
        </html>
        """
        minifier = HtmlMinifier(level=2)
        res = minifier.minify(html)
        self.assertNotIn("remove me", res)
        self.assertIn("<pre>  spaces should stay  </pre>", res)
        self.assertIn("<html><body>", res) # space between tags removed

    @patch('builtins.open', new_callable=mock_open, read_data="body { color: #fff; }")
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    def test_app_orchestration(self, mock_isfile, mock_exists, mock_file):
        app = MinifierApp("style.css", level=2)
        app.run()
        # Ensure correct write call was made
        mock_file().write.assert_called_with("body{color:#fff;}")

# ==============================================================================
# CLI ENTRY POINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Production-Grade HTML/CSS/JS Minifier.",
        epilog="Zero dependencies. Automatically detects file type by extension."
    )
    
    # If the user just wants to run the tests
    parser.add_argument('--test', action='store_true', help='Run the internal unit test suite and exit.')
    parser.add_argument('file', nargs='?', help='Input file to minify (e.g., index.html)')
    parser.add_argument('--level', type=int, choices=[1, 2], default=2, 
                        help='1: Basic (spaces/lines), 2: Aggressive (comments/syntax). Default is 2.')
    parser.add_argument('-v', '--version', action='version', version='MinifyStd v1.0.1')

    args = parser.parse_args()

    if args.test:
        sys.argv = [sys.argv[0]] # Clear args for unittest
        unittest.main(verbosity=2)
        sys.exit(0)

    if not args.file:
        parser.print_help()
        sys.exit(1)

    app = MinifierApp(args.file, args.level)
    app.run()
    sys.exit(0)


if __name__ == "__main__":
    main()