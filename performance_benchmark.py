#!/usr/bin/env python3
"""
Performance Benchmark Script for Document AI Processing

This script compares sequential vs parallel processing performance
and generates comprehensive reports for analysis.
"""

import os
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.parallel_extractor import ParallelTableExtractor


class PerformanceBenchmark:
    """Performance benchmarking suite for Document AI processing."""
    
    def __init__(self, input_folder: str = "inputs"):
        """
        Initialize the benchmark suite.
        
        Args:
            input_folder: Folder containing test images
        """
        self.input_folder = input_folder
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create benchmark output directory
        self.benchmark_dir = f"benchmarks/{self.timestamp}"
        os.makedirs(self.benchmark_dir, exist_ok=True)
        
        print(f"🎯 Performance Benchmark Suite")
        print(f"📁 Results will be saved to: {self.benchmark_dir}")
        print("=" * 60)
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """
        Run comprehensive performance benchmarks.
        
        Returns:
            Dictionary containing all benchmark results
        """
        print("🚀 Starting Comprehensive Performance Benchmark...")
        
        # Test different worker configurations
        worker_configs = [1, 2, 3, 5, 8, 10]
        
        all_results = {}
        
        for workers in worker_configs:
            print(f"\n📊 Testing with {workers} worker(s)...")
            
            if workers == 1:
                # Sequential processing
                extractor = ParallelTableExtractor(max_workers=1)
                result = extractor.process_folder_sequential(
                    self.input_folder, 
                    f"{self.benchmark_dir}/output_sequential"
                )
                result['processing_type'] = 'Sequential'
            else:
                # Parallel processing
                extractor = ParallelTableExtractor(max_workers=workers)
                result = extractor.process_folder_parallel(
                    self.input_folder,
                    f"{self.benchmark_dir}/output_parallel_{workers}"
                )
                result['processing_type'] = 'Parallel'
            
            all_results[f"workers_{workers}"] = result
            
            # Print summary
            if result['success']:
                print(f"  ✅ Completed in {result['total_time']:.2f}s")
                print(f"  📈 Throughput: {result['throughput']:.2f} files/sec")
                print(f"  🎯 Success Rate: {result['successful']}/{result['total_files']}")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Save raw results
        self._save_raw_results(all_results)
        
        # Generate analysis
        analysis = self._analyze_results(all_results)
        
        # Generate visualizations
        self._generate_visualizations(all_results)
        
        # Generate report
        self._generate_report(all_results, analysis)
        
        self.results = all_results
        return all_results
    
    def _save_raw_results(self, results: Dict[str, Any]) -> None:
        """Save raw benchmark results to JSON."""
        output_file = f"{self.benchmark_dir}/raw_results.json"
        
        # Convert results to JSON-serializable format
        json_results = {}
        for key, result in results.items():
            json_result = result.copy()
            
            # Convert ProcessingResult objects to dictionaries
            if 'results' in json_result:
                json_result['results'] = [
                    {
                        'file_path': r.file_path,
                        'success': r.success,
                        'processing_time': r.processing_time,
                        'error': r.error,
                        'tables_count': r.tables_count,
                        'pages_count': r.pages_count,
                        'file_size_mb': r.file_size_mb
                    }
                    for r in json_result['results']
                ]
            
            json_results[key] = json_result
        
        with open(output_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"💾 Raw results saved to: {output_file}")
    
    def _analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze benchmark results and calculate key metrics."""
        analysis = {
            'summary': {},
            'performance_metrics': {},
            'scalability_analysis': {},
            'efficiency_metrics': {}
        }
        
        # Extract key metrics
        worker_counts = []
        total_times = []
        throughputs = []
        success_rates = []
        
        for key, result in results.items():
            if result['success']:
                workers = result['max_workers']
                worker_counts.append(workers)
                total_times.append(result['total_time'])
                throughputs.append(result['throughput'])
                success_rates.append(result['successful'] / result['total_files'])
        
        # Performance metrics
        sequential_time = results['workers_1']['total_time']
        best_parallel_time = min(total_times[1:]) if len(total_times) > 1 else sequential_time
        max_speedup = sequential_time / best_parallel_time if best_parallel_time > 0 else 1
        
        analysis['performance_metrics'] = {
            'sequential_time': sequential_time,
            'best_parallel_time': best_parallel_time,
            'max_speedup': max_speedup,
            'max_throughput': max(throughputs),
            'avg_success_rate': statistics.mean(success_rates) if success_rates else 0
        }
        
        # Scalability analysis
        if len(worker_counts) > 1:
            # Calculate efficiency (speedup / workers)
            efficiencies = []
            speedups = []
            
            for i, workers in enumerate(worker_counts[1:], 1):
                speedup = sequential_time / total_times[i] if total_times[i] > 0 else 1
                efficiency = speedup / workers
                speedups.append(speedup)
                efficiencies.append(efficiency)
            
            analysis['scalability_analysis'] = {
                'speedups': speedups,
                'efficiencies': efficiencies,
                'optimal_workers': worker_counts[1:][efficiencies.index(max(efficiencies))] if efficiencies else 1,
                'linear_speedup_deviation': self._calculate_linearity_deviation(worker_counts[1:], speedups)
            }
        
        # Summary
        total_files = results['workers_1']['total_files']
        total_size_mb = results['workers_1']['total_file_size_mb']
        
        analysis['summary'] = {
            'total_files_processed': total_files,
            'total_data_size_mb': total_size_mb,
            'worker_configurations_tested': len(worker_counts),
            'best_configuration': f"{worker_counts[throughputs.index(max(throughputs))]} workers",
            'performance_improvement': f"{max_speedup:.2f}x faster than sequential",
            'time_saved': f"{sequential_time - best_parallel_time:.2f} seconds"
        }
        
        return analysis
    
    def _calculate_linearity_deviation(self, workers: List[int], speedups: List[float]) -> float:
        """Calculate how much the speedup deviates from linear scaling."""
        if not workers or not speedups:
            return 0.0
        
        # Calculate expected linear speedups
        linear_speedups = workers
        
        # Calculate mean absolute deviation from linear
        deviations = [abs(actual - expected) for actual, expected in zip(speedups, linear_speedups)]
        return statistics.mean(deviations)
    
    def _generate_visualizations(self, results: Dict[str, Any]) -> None:
        """Generate performance visualization charts."""
        try:
            # Set style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # Prepare data
            data = []
            for key, result in results.items():
                if result['success']:
                    data.append({
                        'Workers': result['max_workers'],
                        'Total Time (s)': result['total_time'],
                        'Throughput (files/s)': result['throughput'],
                        'Success Rate': result['successful'] / result['total_files'],
                        'Processing Type': 'Sequential' if result['max_workers'] == 1 else 'Parallel'
                    })
            
            df = pd.DataFrame(data)
            
            # Create subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Document AI Processing Performance Analysis', fontsize=16, fontweight='bold')
            
            # 1. Processing Time vs Workers
            sns.lineplot(data=df, x='Workers', y='Total Time (s)', marker='o', linewidth=3, ax=ax1)
            ax1.set_title('Processing Time vs Number of Workers', fontweight='bold')
            ax1.set_xlabel('Number of Workers')
            ax1.set_ylabel('Total Processing Time (seconds)')
            ax1.grid(True, alpha=0.3)
            
            # 2. Throughput vs Workers
            sns.lineplot(data=df, x='Workers', y='Throughput (files/s)', marker='s', linewidth=3, ax=ax2)
            ax2.set_title('Throughput vs Number of Workers', fontweight='bold')
            ax2.set_xlabel('Number of Workers')
            ax2.set_ylabel('Throughput (files/second)')
            ax2.grid(True, alpha=0.3)
            
            # 3. Speedup Analysis
            sequential_time = df[df['Workers'] == 1]['Total Time (s)'].iloc[0]
            df['Speedup'] = sequential_time / df['Total Time (s)']
            df['Linear Speedup'] = df['Workers']
            
            ax3.plot(df['Workers'], df['Speedup'], 'o-', linewidth=3, label='Actual Speedup', markersize=8)
            ax3.plot(df['Workers'], df['Linear Speedup'], '--', linewidth=2, label='Linear Speedup', alpha=0.7)
            ax3.set_title('Speedup Analysis', fontweight='bold')
            ax3.set_xlabel('Number of Workers')
            ax3.set_ylabel('Speedup Factor')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. Efficiency Analysis
            df['Efficiency'] = df['Speedup'] / df['Workers']
            sns.barplot(data=df, x='Workers', y='Efficiency', ax=ax4)
            ax4.set_title('Parallel Efficiency', fontweight='bold')
            ax4.set_xlabel('Number of Workers')
            ax4.set_ylabel('Efficiency (Speedup/Workers)')
            ax4.grid(True, alpha=0.3)
            
            # Add horizontal line at 100% efficiency
            ax4.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='100% Efficiency')
            ax4.legend()
            
            plt.tight_layout()
            
            # Save plot
            chart_path = f"{self.benchmark_dir}/performance_charts.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Performance charts saved to: {chart_path}")
            
        except ImportError:
            print("⚠️  Matplotlib/Seaborn not available. Skipping visualizations.")
            print("   Install with: pip install matplotlib seaborn pandas")
        except Exception as e:
            print(f"⚠️  Error generating visualizations: {e}")
    
    def _generate_report(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Generate comprehensive performance report."""
        report_path = f"{self.benchmark_dir}/PERFORMANCE_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# Document AI Processing Performance Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            summary = analysis['summary']
            f.write(f"- **Total Files Processed:** {summary['total_files_processed']}\n")
            f.write(f"- **Total Data Size:** {summary['total_data_size_mb']:.2f} MB\n")
            f.write(f"- **Worker Configurations Tested:** {summary['worker_configurations_tested']}\n")
            f.write(f"- **Best Configuration:** {summary['best_configuration']}\n")
            f.write(f"- **Performance Improvement:** {summary['performance_improvement']}\n")
            f.write(f"- **Time Saved:** {summary['time_saved']}\n\n")
            
            # Performance Metrics
            f.write("## 🚀 Performance Metrics\n\n")
            metrics = analysis['performance_metrics']
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Sequential Processing Time | {metrics['sequential_time']:.2f}s |\n")
            f.write(f"| Best Parallel Processing Time | {metrics['best_parallel_time']:.2f}s |\n")
            f.write(f"| Maximum Speedup | {metrics['max_speedup']:.2f}x |\n")
            f.write(f"| Maximum Throughput | {metrics['max_throughput']:.2f} files/sec |\n")
            f.write(f"| Average Success Rate | {metrics['avg_success_rate']*100:.1f}% |\n\n")
            
            # Detailed Results
            f.write("## 📈 Detailed Results\n\n")
            f.write("| Workers | Processing Type | Total Time (s) | Throughput (files/s) | Speedup | Efficiency |\n")
            f.write("|---------|----------------|----------------|---------------------|---------|------------|\n")
            
            sequential_time = results['workers_1']['total_time']
            for key, result in results.items():
                if result['success']:
                    workers = result['max_workers']
                    processing_type = result['processing_type']
                    total_time = result['total_time']
                    throughput = result['throughput']
                    speedup = sequential_time / total_time if total_time > 0 else 1
                    efficiency = speedup / workers if workers > 0 else 0
                    
                    f.write(f"| {workers} | {processing_type} | {total_time:.2f} | {throughput:.2f} | {speedup:.2f}x | {efficiency:.2f} |\n")
            
            f.write("\n")
            
            # Scalability Analysis
            if 'scalability_analysis' in analysis:
                f.write("## 📊 Scalability Analysis\n\n")
                scalability = analysis['scalability_analysis']
                f.write(f"- **Optimal Worker Count:** {scalability['optimal_workers']}\n")
                f.write(f"- **Linear Speedup Deviation:** {scalability['linear_speedup_deviation']:.2f}\n")
                f.write("- **Speedup Pattern:** ")
                if scalability['linear_speedup_deviation'] < 0.5:
                    f.write("Near-linear scaling achieved ✅\n")
                elif scalability['linear_speedup_deviation'] < 1.0:
                    f.write("Good scaling with some overhead ⚠️\n")
                else:
                    f.write("Diminishing returns observed ❌\n")
                f.write("\n")
            
            # File-Level Analysis
            f.write("## 📁 File-Level Performance Analysis\n\n")
            
            # Get results from best performing configuration
            best_result = max(results.values(), key=lambda x: x.get('throughput', 0))
            if 'results' in best_result:
                f.write("### Processing Time by File\n\n")
                f.write("| File | Size (MB) | Processing Time (s) | Tables Found | Status |\n")
                f.write("|------|-----------|-------------------|--------------|--------|\n")
                
                for file_result in best_result['results']:
                    filename = os.path.basename(file_result.file_path)
                    status = "✅ Success" if file_result.success else f"❌ {file_result.error}"
                    f.write(f"| {filename} | {file_result.file_size_mb} | {file_result.processing_time:.2f} | {file_result.tables_count} | {status} |\n")
                
                f.write("\n")
            
            # Recommendations
            f.write("## 💡 Recommendations\n\n")
            f.write("### Production Deployment\n")
            f.write(f"- **Recommended Worker Count:** {analysis['scalability_analysis']['optimal_workers']} workers for optimal efficiency\n")
            f.write("- **Expected Processing Time:** ")
            
            optimal_workers = analysis['scalability_analysis']['optimal_workers']
            optimal_result = results.get(f'workers_{optimal_workers}')
            if optimal_result:
                f.write(f"{optimal_result['total_time']:.2f}s for {optimal_result['total_files']} files\n")
            
            f.write("- **Memory Requirements:** ~512MB per worker recommended\n")
            f.write("- **API Rate Limiting:** Consider Google Cloud Document AI quotas\n\n")
            
            f.write("### Scaling Considerations\n")
            f.write("- **I/O Bound Nature:** Document AI processing is primarily I/O-bound (API calls)\n")
            f.write("- **Thread Pool Advantage:** ThreadPoolExecutor is optimal for this workload\n")
            f.write("- **Network Latency:** Performance may vary based on network conditions\n")
            f.write("- **API Quotas:** Monitor Google Cloud API usage and quotas\n\n")
            
            # Technical Details
            f.write("## 🔧 Technical Implementation\n\n")
            f.write("### Architecture\n")
            f.write("- **Framework:** Python ThreadPoolExecutor\n")
            f.write("- **API Integration:** Google Cloud Document AI\n")
            f.write("- **Concurrency Model:** Thread-based parallelism for I/O-bound operations\n")
            f.write("- **Error Handling:** Individual file error isolation\n")
            f.write("- **Progress Tracking:** Real-time processing status\n\n")
            
            f.write("### Performance Characteristics\n")
            f.write("- **Processing Pattern:** Batch processing with configurable parallelism\n")
            f.write("- **Resource Usage:** Low CPU, moderate memory, high network I/O\n")
            f.write("- **Scalability:** Horizontal scaling via worker count adjustment\n")
            f.write("- **Fault Tolerance:** Individual file failures don't affect batch\n\n")
            
            # Conclusion
            f.write("## 🎯 Conclusion\n\n")
            improvement_pct = (metrics['max_speedup'] - 1) * 100
            f.write(f"The parallel processing implementation achieved a **{metrics['max_speedup']:.2f}x speedup** ")
            f.write(f"({improvement_pct:.1f}% improvement) over sequential processing. ")
            f.write("This demonstrates the effectiveness of parallel processing for I/O-bound Document AI operations.\n\n")
            
            f.write("The implementation successfully processes multiple documents concurrently while maintaining ")
            f.write("error isolation and providing comprehensive progress tracking. The thread-based approach is ")
            f.write("well-suited for the I/O-bound nature of Document AI API calls.\n\n")
            
            f.write("---\n")
            f.write(f"*Report generated by Document AI Performance Benchmark Suite - {self.timestamp}*\n")
        
        print(f"📄 Performance report saved to: {report_path}")


def main():
    """Run the performance benchmark suite."""
    print("🎯 Document AI Performance Benchmark Suite")
    print("=" * 60)
    
    # Check if input folder exists
    if not os.path.exists("inputs"):
        print("❌ Error: 'inputs' folder not found!")
        print("   Please ensure you have images in the 'inputs' folder.")
        return
    
    # Count files
    supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf'}
    files = [f for f in os.listdir("inputs") 
             if os.path.splitext(f)[1].lower() in supported_extensions]
    
    if not files:
        print("❌ Error: No supported image files found in 'inputs' folder!")
        return
    
    print(f"📁 Found {len(files)} files to process")
    print(f"🎯 This benchmark will test different worker configurations")
    print("   and generate comprehensive performance analysis.\n")
    
    # Initialize and run benchmark
    benchmark = PerformanceBenchmark("inputs")
    results = benchmark.run_comprehensive_benchmark()
    
    print("\n🎉 Benchmark Complete!")
    print(f"📊 Results saved in: {benchmark.benchmark_dir}")
    print("📄 Check PERFORMANCE_REPORT.md for detailed analysis")


if __name__ == "__main__":
    main()
