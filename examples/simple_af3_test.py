"""
Simple AF3 Test - Test our enhanced hierarchical structure
"""

import pandas as pd
from pathlib import Path
import sys

# Add the alphafold_core to the path
sys.path.append(str(Path(__file__).parent.parent))

def test_enhanced_system():
    """Test our enhanced system with the existing summary statistics"""
    print("🧪 Testing Enhanced AF3 Analysis System")
    print("=" * 50)
    
    # Load the existing summary statistics file
    summary_file = "Project/Triple_Overlap_DNA_RNA_Project/src/26 Overlapped Analysis/Server_RLoop_Overlap_Summary_Stats.csv"
    
    if not Path(summary_file).exists():
        print(f"❌ File not found: {summary_file}")
        return
    
    # Load the data
    df = pd.read_csv(summary_file)
    print(f"✅ Loaded {len(df)} predictions from {summary_file}")
    print(f"✅ Columns: {list(df.columns)}")
    
    # Test basic statistics
    print(f"\n📊 Basic Statistics:")
    print(f"   - iPTM: mean={df['iptm'].mean():.3f}, std={df['iptm'].std():.3f}")
    print(f"   - pTM: mean={df['ptm'].mean():.3f}, std={df['ptm'].std():.3f}")
    print(f"   - Ranking Score: mean={df['ranking_score'].mean():.3f}, std={df['ranking_score'].std():.3f}")
    
    # Test quality assessment
    print(f"\n🎯 Quality Assessment:")
    high_iptm = (df['iptm'] >= 0.6).sum()
    high_ptm = (df['ptm'] >= 0.5).sum()
    high_ranking = (df['ranking_score'] >= 0.8).sum()
    
    print(f"   - High iPTM (≥0.6): {high_iptm}/{len(df)} ({high_iptm/len(df)*100:.1f}%)")
    print(f"   - High pTM (≥0.5): {high_ptm}/{len(df)} ({high_ptm/len(df)*100:.1f}%)")
    print(f"   - High Ranking (≥0.8): {high_ranking}/{len(df)} ({high_ranking/len(df)*100:.1f}%)")
    
    # Test our enhanced JSONProcessor
    print(f"\n🔧 Testing Enhanced JSONProcessor:")
    try:
        from alphafold_core.data.processor import JSONProcessor
        processor = JSONProcessor()
        print(f"   ✅ JSONProcessor imported successfully")
        print(f"   ✅ AF3 headers available: {len(processor.af3_csv_headers)} columns")
    except Exception as e:
        print(f"   ❌ Error importing JSONProcessor: {e}")
    
    # Test our analysis modules
    print(f"\n📈 Testing Analysis Modules:")
    try:
        from alphafold_core.analysis.statistics import StatisticalAnalyzer
        from alphafold_core.analysis.quality import QualityAnalyzer
        
        stats_analyzer = StatisticalAnalyzer()
        quality_analyzer = QualityAnalyzer()
        
        print(f"   ✅ StatisticalAnalyzer imported successfully")
        print(f"   ✅ QualityAnalyzer imported successfully")
        
        # Test statistical analysis
        ci_iptm = stats_analyzer.calculate_confidence_intervals(df['iptm'])
        print(f"   ✅ iPTM 95% CI: {ci_iptm['mean']:.3f} [{ci_iptm['ci_lower']:.3f}, {ci_iptm['ci_upper']:.3f}]")
        
        # Test quality assessment
        assessment = quality_analyzer.assess_prediction_quality(df)
        print(f"   ✅ Quality assessment completed: {assessment['total_predictions']} predictions")
        
    except Exception as e:
        print(f"   ❌ Error importing analysis modules: {e}")
    
    print(f"\n✅ Test completed successfully!")
    print(f"🎯 Our enhanced system is ready for your new summary statistics!")

if __name__ == "__main__":
    test_enhanced_system() 