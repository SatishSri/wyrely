"""
Parallel Document AI Table Extractor

This module implements parallel processing for Document AI table extraction
using ThreadPoolExecutor for improved performance on batch operations.
"""

import os
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from threading import Lock
import logging
from dataclasses import dataclass
from datetime import datetime

from .extractor import TableExtractor


@dataclass
class ProcessingResult:
    """Result of processing a single document."""
    file_path: str
    success: bool
    processing_time: float
    error: Optional[str] = None
    tables_count: int = 0
    pages_count: int = 0
    file_size_mb: float = 0.0


class ParallelTableExtractor(TableExtractor):
    """
    Parallel version of TableExtractor using ThreadPoolExecutor.
    
    This class extends the base TableExtractor to add parallel processing
    capabilities for batch document processing.
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize the parallel extractor.
        
        Args:
            max_workers: Maximum number of parallel threads (default: 5)
        """
        super().__init__()
        self.max_workers = max_workers
        self.results_lock = Lock()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the parallel extractor."""
        logger = logging.getLogger('ParallelExtractor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB."""
        try:
            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.0
    
    def _process_single_file(self, file_path: str, output_folder: str) -> ProcessingResult:
        """
        Process a single file and return timing information.
        
        Args:
            file_path: Path to the input file
            output_folder: Path to save output
            
        Returns:
            ProcessingResult object with timing and result information
        """
        start_time = time.time()
        filename = os.path.basename(file_path)
        file_size = self._get_file_size_mb(file_path)
        
        try:
            self.logger.info(f"🔄 Processing: {filename}")
            
            # Process the document
            result = self.extract_tables(file_path)
            
            if result['success']:
                # Generate output filename
                base_name = os.path.splitext(filename)[0]
                output_filename = f"{base_name}_extracted.txt"
                output_path = os.path.join(output_folder, output_filename)
                
                # Save result
                self._save_result(result, output_path)
                
                processing_time = time.time() - start_time
                
                self.logger.info(f"✅ Completed: {filename} ({processing_time:.2f}s)")
                
                return ProcessingResult(
                    file_path=file_path,
                    success=True,
                    processing_time=processing_time,
                    tables_count=len(result['tables']),
                    pages_count=result['pages'],
                    file_size_mb=file_size
                )
            else:
                processing_time = time.time() - start_time
                error_msg = result.get('error', 'Unknown error')
                
                self.logger.error(f"❌ Failed: {filename} - {error_msg}")
                
                return ProcessingResult(
                    file_path=file_path,
                    success=False,
                    processing_time=processing_time,
                    error=error_msg,
                    file_size_mb=file_size
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            self.logger.error(f"💥 Exception: {filename} - {error_msg}")
            
            return ProcessingResult(
                file_path=file_path,
                success=False,
                processing_time=processing_time,
                error=error_msg,
                file_size_mb=file_size
            )
    
    def _save_result(self, result: Dict[str, Any], output_path: str) -> None:
        """Save extraction result to file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("DOCUMENT AI TABLE EXTRACTION RESULTS\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Pages: {result['pages']}\n")
                f.write(f"Tables Found: {len(result['tables'])}\n")
                f.write(f"Processor: {result['processor']}\n\n")
                
                if result['tables']:
                    f.write("EXTRACTED TABLES:\n")
                    f.write("-" * 40 + "\n")
                    for i, table in enumerate(result['tables'], 1):
                        f.write(f"\nTable {i}:\n")
                        for row in table:
                            f.write(" | ".join(str(cell) for cell in row) + "\n")
                        f.write("\n")
                
                f.write("\nFULL TEXT CONTENT:\n")
                f.write("-" * 40 + "\n")
                f.write(result['text'])
                
        except Exception as e:
            self.logger.error(f"Failed to save result to {output_path}: {e}")
    
    def process_folder_parallel(self, input_folder: str = "inputs", 
                              output_folder: str = "outputs") -> Dict[str, Any]:
        """
        Process all images in a folder using parallel processing.
        
        Args:
            input_folder: Folder containing input images
            output_folder: Folder to save output files
            
        Returns:
            Dictionary with processing results and performance metrics
        """
        start_time = time.time()
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Find all supported files
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf'}
        image_files = []
        
        if os.path.exists(input_folder):
            for filename in os.listdir(input_folder):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in supported_extensions:
                    image_files.append(os.path.join(input_folder, filename))
        
        if not image_files:
            return {
                'success': False,
                'error': f'No supported files found in {input_folder}',
                'processed': 0,
                'results': []
            }
        
        self.logger.info(f"🚀 Starting parallel processing of {len(image_files)} files with {self.max_workers} workers")
        
        # Process files in parallel
        results = []
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_single_file, file_path, output_folder): file_path
                for file_path in image_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)
                
                if result.success:
                    successful += 1
                else:
                    failed += 1
                
                # Progress update
                completed = successful + failed
                progress = (completed / len(image_files)) * 100
                self.logger.info(f"📊 Progress: {completed}/{len(image_files)} ({progress:.1f}%)")
        
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        total_processing_time = sum(r.processing_time for r in results)
        avg_processing_time = total_processing_time / len(results) if results else 0
        total_file_size = sum(r.file_size_mb for r in results)
        throughput = len(results) / total_time if total_time > 0 else 0
        
        self.logger.info(f"🎉 Parallel processing completed in {total_time:.2f}s")
        self.logger.info(f"📈 Throughput: {throughput:.2f} files/second")
        
        return {
            'success': True,
            'total_files': len(image_files),
            'successful': successful,
            'failed': failed,
            'total_time': total_time,
            'total_processing_time': total_processing_time,
            'avg_processing_time': avg_processing_time,
            'total_file_size_mb': total_file_size,
            'throughput': throughput,
            'max_workers': self.max_workers,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_folder_sequential(self, input_folder: str = "inputs",
                                output_folder: str = "outputs") -> Dict[str, Any]:
        """
        Process all images in a folder sequentially (for comparison).
        
        Args:
            input_folder: Folder containing input images
            output_folder: Folder to save output files
            
        Returns:
            Dictionary with processing results and performance metrics
        """
        start_time = time.time()
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Find all supported files
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf'}
        image_files = []
        
        if os.path.exists(input_folder):
            for filename in os.listdir(input_folder):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in supported_extensions:
                    image_files.append(os.path.join(input_folder, filename))
        
        if not image_files:
            return {
                'success': False,
                'error': f'No supported files found in {input_folder}',
                'processed': 0,
                'results': []
            }
        
        self.logger.info(f"🐌 Starting sequential processing of {len(image_files)} files")
        
        # Process files sequentially
        results = []
        successful = 0
        failed = 0
        
        for i, file_path in enumerate(image_files, 1):
            self.logger.info(f"📝 Processing file {i}/{len(image_files)}")
            
            result = self._process_single_file(file_path, output_folder)
            results.append(result)
            
            if result.success:
                successful += 1
            else:
                failed += 1
            
            # Progress update
            progress = (i / len(image_files)) * 100
            self.logger.info(f"📊 Progress: {i}/{len(image_files)} ({progress:.1f}%)")
        
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        total_processing_time = sum(r.processing_time for r in results)
        avg_processing_time = total_processing_time / len(results) if results else 0
        total_file_size = sum(r.file_size_mb for r in results)
        throughput = len(results) / total_time if total_time > 0 else 0
        
        self.logger.info(f"🏁 Sequential processing completed in {total_time:.2f}s")
        self.logger.info(f"📈 Throughput: {throughput:.2f} files/second")
        
        return {
            'success': True,
            'total_files': len(image_files),
            'successful': successful,
            'failed': failed,
            'total_time': total_time,
            'total_processing_time': total_processing_time,
            'avg_processing_time': avg_processing_time,
            'total_file_size_mb': total_file_size,
            'throughput': throughput,
            'max_workers': 1,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """
    Main function to demonstrate parallel vs sequential processing.
    """
    print("🚀 Document AI Parallel Processing Demo")
    print("=" * 50)
    
    extractor = ParallelTableExtractor(max_workers=5)
    
    print("\n1. Running Sequential Processing...")
    sequential_results = extractor.process_folder_sequential("inputs", "outputs/sequential")
    
    print("\n2. Running Parallel Processing...")
    parallel_results = extractor.process_folder_parallel("inputs", "outputs/parallel")
    
    print("\n📊 PERFORMANCE COMPARISON")
    print("=" * 50)
    print(f"Sequential Time: {sequential_results['total_time']:.2f}s")
    print(f"Parallel Time:   {parallel_results['total_time']:.2f}s")
    
    if sequential_results['total_time'] > 0:
        speedup = sequential_results['total_time'] / parallel_results['total_time']
        print(f"Speedup:         {speedup:.2f}x")
        print(f"Time Saved:      {sequential_results['total_time'] - parallel_results['total_time']:.2f}s")


if __name__ == "__main__":
    main()
