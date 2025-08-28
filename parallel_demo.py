#!/usr/bin/env python3
"""
Parallel Processing Demo for Document AI

This script demonstrates the difference between sequential and parallel
processing for Document AI table extraction.
"""

import os
import sys
import time
from src.parallel_extractor import ParallelTableExtractor


def print_banner():
    """Print demo banner."""
    print("🚀 Document AI Parallel Processing Demo")
    print("=" * 50)
    print("This demo compares sequential vs parallel processing")
    print("for Document AI table extraction.\n")


def check_prerequisites():
    """Check if prerequisites are met."""
    if not os.path.exists("inputs"):
        print("❌ Error: 'inputs' folder not found!")
        print("   Please create an 'inputs' folder with images to process.")
        return False
    
    # Check for supported files
    supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf'}
    files = [f for f in os.listdir("inputs") 
             if os.path.splitext(f)[1].lower() in supported_extensions]
    
    if not files:
        print("❌ Error: No supported files found in 'inputs' folder!")
        print("   Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, PDF")
        return False
    
    print(f"✅ Found {len(files)} files to process:")
    for file in files[:5]:  # Show first 5 files
        print(f"   - {file}")
    if len(files) > 5:
        print(f"   ... and {len(files) - 5} more files")
    print()
    
    return True


def run_comparison_demo():
    """Run the sequential vs parallel comparison demo."""
    print("🎯 Running Performance Comparison Demo\n")
    
    # Initialize extractor
    extractor = ParallelTableExtractor(max_workers=5)
    
    # Create output directories
    os.makedirs("outputs/demo_sequential", exist_ok=True)
    os.makedirs("outputs/demo_parallel", exist_ok=True)
    
    print("1️⃣ Running Sequential Processing...")
    print("-" * 40)
    start_time = time.time()
    
    sequential_results = extractor.process_folder_sequential(
        "inputs", 
        "outputs/demo_sequential"
    )
    
    sequential_time = time.time() - start_time
    print(f"   ⏱️  Sequential completed in: {sequential_time:.2f}s")
    print(f"   📊 Files processed: {sequential_results['successful']}/{sequential_results['total_files']}")
    print(f"   📈 Throughput: {sequential_results['throughput']:.2f} files/sec\n")
    
    print("2️⃣ Running Parallel Processing (5 workers)...")
    print("-" * 40)
    start_time = time.time()
    
    parallel_results = extractor.process_folder_parallel(
        "inputs",
        "outputs/demo_parallel"
    )
    
    parallel_time = time.time() - start_time
    print(f"   ⏱️  Parallel completed in: {parallel_time:.2f}s")
    print(f"   📊 Files processed: {parallel_results['successful']}/{parallel_results['total_files']}")
    print(f"   📈 Throughput: {parallel_results['throughput']:.2f} files/sec\n")
    
    # Performance comparison
    print("📊 PERFORMANCE COMPARISON")
    print("=" * 50)
    print(f"Sequential Time:     {sequential_time:.2f}s")
    print(f"Parallel Time:       {parallel_time:.2f}s")
    
    if sequential_time > 0 and parallel_time > 0:
        speedup = sequential_time / parallel_time
        time_saved = sequential_time - parallel_time
        improvement_pct = (speedup - 1) * 100
        
        print(f"Speedup:             {speedup:.2f}x")
        print(f"Time Saved:          {time_saved:.2f}s")
        print(f"Performance Gain:    {improvement_pct:.1f}%")
        
        if speedup > 2:
            print("🎉 Excellent parallel performance!")
        elif speedup > 1.5:
            print("✅ Good parallel performance!")
        else:
            print("⚠️  Limited parallel benefit (small dataset or overhead)")
    
    print(f"\n📁 Results saved to:")
    print(f"   - Sequential: outputs/demo_sequential/")
    print(f"   - Parallel:   outputs/demo_parallel/")
    
    return sequential_results, parallel_results


def run_scalability_test():
    """Run a quick scalability test with different worker counts."""
    print("\n🔬 Running Scalability Test")
    print("=" * 50)
    print("Testing different worker configurations...\n")
    
    worker_configs = [1, 2, 3, 5]
    results = {}
    
    for workers in worker_configs:
        print(f"Testing {workers} worker(s)...")
        
        extractor = ParallelTableExtractor(max_workers=workers)
        
        if workers == 1:
            result = extractor.process_folder_sequential(
                "inputs",
                f"outputs/scale_test_{workers}"
            )
        else:
            result = extractor.process_folder_parallel(
                "inputs",
                f"outputs/scale_test_{workers}"
            )
        
        results[workers] = result
        
        if result['success']:
            print(f"   ⏱️  Time: {result['total_time']:.2f}s")
            print(f"   📈 Throughput: {result['throughput']:.2f} files/sec\n")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}\n")
    
    # Display scalability results
    print("📊 Scalability Results:")
    print("-" * 30)
    print("Workers | Time (s) | Speedup | Efficiency")
    print("--------|----------|---------|----------")
    
    baseline_time = results[1]['total_time']
    
    for workers in worker_configs:
        if results[workers]['success']:
            time_taken = results[workers]['total_time']
            speedup = baseline_time / time_taken if time_taken > 0 else 1
            efficiency = speedup / workers if workers > 0 else 0
            
            print(f"   {workers:2d}   |  {time_taken:6.2f}  |  {speedup:5.2f}x  |   {efficiency:5.2f}")
    
    return results


def main():
    """Main demo function."""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    try:
        # Run comparison demo
        sequential_results, parallel_results = run_comparison_demo()
        
        # Ask if user wants to run scalability test
        print("\n" + "="*50)
        response = input("Would you like to run a scalability test? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            run_scalability_test()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next Steps:")
        print("   - Run 'python3 performance_benchmark.py' for comprehensive analysis")
        print("   - Check the outputs/ folder for extracted table data")
        print("   - Review the processing logs for detailed information")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("   Please check your environment configuration and try again.")


if __name__ == "__main__":
    main()
