#!/usr/bin/env python3
"""
Simple script to generate the car dataset
"""

from CarAnalyzer import CarAnalyzer

def main():
    print("🚗 Car Dataset Generator")
    print("=" * 50)
    
    # Create analyzer
    analyzer = CarAnalyzer()
    
    # Generate sample data
    print("Creating comprehensive car dataset...")
    analyzer.listings = analyzer.create_sample_data()
    
    # Analyze the data
    df_analyzed = analyzer.analyze_data()
    
    if df_analyzed is not None and not df_analyzed.empty:
        # Save dataset
        success = analyzer.save_dataset(df_analyzed)
        
        if success:
            # Show summary
            analyzer.get_dataset_summary(df_analyzed)
            print("\n✅ Dataset generation completed successfully!")
            print(f"📁 Dataset saved as: {analyzer.dataset_file}")
        else:
            print("❌ Failed to save dataset!")
    else:
        print("❌ No valid data to analyze!")

if __name__ == "__main__":
    main()
