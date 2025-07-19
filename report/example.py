"""Example usage of the report module."""

from pathlib import Path
from .processor import ReportProcessor


def run_example():
    """Run example processing of report files."""
    # Define paths
    current_dir = Path(__file__).parent.parent
    report_dir = current_dir / 'reportFile'
    output_dir = current_dir / 'report_output'
    
    print(f"Report directory: {report_dir}")
    print(f"Output directory: {output_dir}")
    
    try:
        # Create processor
        processor = ReportProcessor(str(report_dir), str(output_dir))
        
        # Process all files
        results = processor.process_all_files()
        
        print("\n" + "="*50)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print("="*50)
        
        print(f"\nResults Summary:")
        print(f"- Total files found: {results['total_files']}")
        print(f"- Successfully processed: {results['processed_files']}")
        print(f"- Failed to process: {results['failed_files']}")
        print(f"- Output files created: {len(results['output_files'])}")
        print(f"- Output directory: {results['output_directory']}")
        
        if results['output_files']:
            print(f"\nGenerated files:")
            for file_path in results['output_files']:
                file_name = Path(file_path).name
                print(f"  - {file_name}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure the reportFile directory exists and contains XML files.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == '__main__':
    run_example()