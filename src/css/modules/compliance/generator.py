"""Compliance report generation and endpoints."""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ComplianceReportGenerator:
    """Generate compliance reports from control mappings."""
    
    def __init__(self):
        pass
    
    async def generate_report(
        self,
        organization_id: int,
        framework_id: int,
        scope: str = "all systems",
    ) -> Dict:
        """
        Generate compliance report for framework.
        
        Calculates:
        - Total controls in framework
        - Compliant / partially compliant / non-compliant counts
        - Overall compliance percentage
        - Risk score
        - Trend vs previous report
        
        Args:
            organization_id: Org to report on
            framework_id: Framework to report on
            scope: Report scope (e.g., "production only")
        
        Returns:
            Report data dict ready for database storage
        """
        from .models import (
            ComplianceFramework,
            FrameworkControl,
            ControlMapping,
            ComplianceReport,
            ComplianceStatus,
        )
        
        try:
            # Get framework
            framework = await ComplianceFramework.get_or_none(
                id=framework_id,
                organization_id=organization_id,
            )
            if not framework:
                raise ValueError("Framework not found")
            
            # Get all controls in framework
            controls = await FrameworkControl.filter(framework_id=framework_id).all()
            total_controls = len(controls)
            
            # Count status distribution
            compliant = 0
            partially_compliant = 0
            non_compliant = 0
            not_applicable = 0
            unknown = 0
            
            for control in controls:
                # Get most recent mapping for this control
                mappings = await ControlMapping.filter(control_id=control.id).order_by("-updated_at").all()
                
                if not mappings:
                    # No mappings = unknown status
                    unknown += 1
                    continue
                
                latest_mapping = mappings[0]
                status = latest_mapping.status
                
                if status == ComplianceStatus.COMPLIANT:
                    compliant += 1
                elif status == ComplianceStatus.PARTIALLY_COMPLIANT:
                    partially_compliant += 1
                elif status == ComplianceStatus.NON_COMPLIANT:
                    non_compliant += 1
                elif status == ComplianceStatus.NOT_APPLICABLE:
                    not_applicable += 1
                else:
                    unknown += 1
            
            # Calculate compliance percentage
            counted_controls = compliant + partially_compliant + non_compliant
            if counted_controls > 0:
                compliance_percentage = (
                    (compliant + 0.5 * partially_compliant) / counted_controls
                ) * 100
            else:
                compliance_percentage = 0.0
            
            # Calculate risk score (0-100, higher = worse)
            risk_score = 100 - compliance_percentage
            
            # Get previous report to calculate trend
            previous_report = await ComplianceReport.filter(
                organization_id=organization_id,
                framework_id=framework_id,
            ).order_by("-generated_at").first()
            
            previous_percentage = None
            trend = "stable"
            if previous_report:
                previous_percentage = previous_report.compliance_percentage
                if compliance_percentage > previous_percentage + 2:
                    trend = "improving"
                elif compliance_percentage < previous_percentage - 2:
                    trend = "declining"
            
            # Create report
            report_data = {
                "organization_id": organization_id,
                "framework_id": framework_id,
                "total_controls": total_controls,
                "compliant_controls": compliant,
                "partially_compliant_controls": partially_compliant,
                "non_compliant_controls": non_compliant,
                "not_applicable_controls": not_applicable,
                "compliance_percentage": round(compliance_percentage, 2),
                "risk_score": round(risk_score, 2),
                "previous_percentage": previous_percentage,
                "trend": trend,
                "scope": scope,
            }
            
            logger.info(
                f"Generated compliance report for org {organization_id} "
                f"framework {framework_id}: {compliance_percentage:.1f}% compliant"
            )
            
            return report_data
        
        except Exception as e:
            logger.exception(f"Failed to generate compliance report: {e}")
            raise


__all__ = ["ComplianceReportGenerator"]
