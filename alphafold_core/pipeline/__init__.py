"""
Pipeline module for AlphaFold Core
Provides high-level workflows that combine multiple operations
"""

from .workflows import (
    ProteinAnalysisPipeline,
    OverlapAnalysisPipeline,
    QualityAssessmentPipeline,
    DataProcessingPipeline,
    GeneToProteinPipeline
)
from .organized_workflows import OrganizedWorkflowManager

__all__ = [
    'ProteinAnalysisPipeline',
    'OverlapAnalysisPipeline', 
    'QualityAssessmentPipeline',
    'DataProcessingPipeline',
    'GeneToProteinPipeline',
    'OrganizedWorkflowManager'
] 