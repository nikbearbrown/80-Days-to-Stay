#!/usr/bin/env python3
"""
Webpage Content Extractor - RAW VERSION
Processes scraped HTML files, extracts ALL text content.
Only removes HTML tags - keeps URLs, timestamps, metadata intact.
USE THIS FOR: Preserving all information, archiving, complete data extraction
"""

import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from typing import List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebpageProcessor:
    def __init__(self, base_path: str, max_workers: int = 4):
        """
        Initialize the webpage processor.
        
        Args:
            base_path: Root path to the websites folder
            max_workers: Number of threads for parallel processing
        """
        self.base_path = Path(base_path)
        self.max_workers = max_workers
        self.processed_files = 0
        self.failed_files = 0
        
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract ALL text content from HTML, removing only HTML tags.
        Preserves URLs, timestamps, metadata, and all other text.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Text content with HTML tags removed
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove only script and style elements (code, not content)
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get ALL text content
            text = soup.get_text(separator='\n', strip=True)
            
            # Basic whitespace cleanup only
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)
            
            # Remove excessive blank lines (more than 2 consecutive)
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            return ""
    
    def process_html_file(self, file_path: Path) -> Tuple[bool, str, str]:
        """
        Process a single HTML file and create corresponding MD file.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            Tuple of (success, markdown_path, extracted_content)
        """
        try:
            # Read HTML file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Extract text content
            text_content = self.extract_text_from_html(html_content)
            
            if not text_content:
                logger.warning(f"No content extracted from {file_path}")
                return False, "", ""
            
            # Create MD file path (same name, different extension)
            md_path = file_path.with_suffix('.md')
            
            # Write to MD file - only the extracted text content
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"Processed: {file_path.name} -> {md_path.name}")
            return True, str(md_path), text_content
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False, "", ""
    
    def create_master_file(self, folder_path: Path, md_contents: List[Tuple[str, str]]):
        """
        Create a master file containing all content from MD files in a folder.
        
        Args:
            folder_path: Path to the folder
            md_contents: List of tuples (file_name, content)
        """
        try:
            folder_name = folder_path.name
            master_file_path = folder_path / f"{folder_name}_all_content.txt"
            
            # Write only the extracted text content, no extra formatting
            with open(master_file_path, 'w', encoding='utf-8') as f:
                for file_name, content in sorted(md_contents):
                    f.write(content)
                    f.write("\n\n")
            
            logger.info(f"Created master file: {master_file_path} ({len(md_contents)} files)")
            
        except Exception as e:
            logger.error(f"Error creating master file for {folder_path}: {e}")
    
    def process_folder(self, folder_path: Path):
        """
        Process all HTML files in a folder using multithreading.
        
        Args:
            folder_path: Path to the folder to process
        """
        # Find all HTML files in the folder (non-recursive for this level)
        html_files = list(folder_path.glob('*.html')) + list(folder_path.glob('*.htm'))
        
        if not html_files:
            logger.info(f"No HTML files found in {folder_path}")
            return
        
        logger.info(f"Processing {len(html_files)} files in {folder_path.name}")
        
        md_contents = []
        
        # Process files using thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_html_file, file_path): file_path 
                for file_path in html_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success, md_path, content = future.result()
                    if success:
                        self.processed_files += 1
                        md_contents.append((file_path.name, content))
                    else:
                        self.failed_files += 1
                except Exception as e:
                    logger.error(f"Exception processing {file_path}: {e}")
                    self.failed_files += 1
        
        # Create master file for this folder
        if md_contents:
            self.create_master_file(folder_path, md_contents)
    
    def process_all(self):
        """
        Process all folders in the base path recursively.
        """
        if not self.base_path.exists():
            logger.error(f"Base path does not exist: {self.base_path}")
            return
        
        logger.info(f"Starting processing of {self.base_path}")
        logger.info(f"Using {self.max_workers} worker threads")
        
        # Get all subdirectories in the websites folder
        subdirs = [d for d in self.base_path.iterdir() if d.is_dir()]
        
        if not subdirs:
            logger.warning(f"No subdirectories found in {self.base_path}")
            return
        
        logger.info(f"Found {len(subdirs)} folders to process")
        
        # Process each subdirectory
        for subdir in subdirs:
            logger.info(f"\n{'*' * 80}")
            logger.info(f"Processing folder: {subdir.name}")
            logger.info(f"{'*' * 80}")
            self.process_folder(subdir)
        
        # Summary
        logger.info(f"\n{'=' * 80}")
        logger.info("Processing Complete!")
        logger.info(f"Successfully processed: {self.processed_files} files")
        logger.info(f"Failed: {self.failed_files} files")
        logger.info(f"{'=' * 80}")


def main():
    """Main entry point for the script."""
    # Determine paths
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    websites_path = base_dir / "websites"
    
    logger.info(f"Script directory: {script_dir}")
    logger.info(f"Websites directory: {websites_path}")
    
    # Create processor and run
    processor = WebpageProcessor(
        base_path=str(websites_path),
        max_workers=4
    )
    
    processor.process_all()


if __name__ == "__main__":
    main()
