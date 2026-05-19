"""
Tests for recommender module.
"""

import pytest
from app.recommender import SafetyRecommender, AlertSeverity


def test_get_recommendations_fire():
    """Test getting recommendations for fire."""
    recs = SafetyRecommender.get_recommendations("fire")
    
    assert len(recs) > 0
    assert isinstance(recs, list)
    assert any("emergency" in rec.lower() for rec in recs)


def test_get_recommendations_smoke():
    """Test getting recommendations for smoke."""
    recs = SafetyRecommender.get_recommendations("smoke")
    
    assert len(recs) > 0
    assert isinstance(recs, list)
    assert any("smoke" in rec.lower() or "source" in rec.lower() for rec in recs)


def test_get_recommendations_unknown():
    """Test getting recommendations for unknown type."""
    recs = SafetyRecommender.get_recommendations("unknown")
    
    assert isinstance(recs, list)
    assert len(recs) == 0


def test_get_severity_fire_high():
    """Test fire severity at high confidence."""
    severity = SafetyRecommender.get_severity("fire", 0.90)
    assert severity == AlertSeverity.CRITICAL


def test_get_severity_fire_threshold():
    """Test fire severity at threshold."""
    severity = SafetyRecommender.get_severity("fire", 0.60)
    assert severity == AlertSeverity.CRITICAL


def test_get_severity_fire_low():
    """Test fire severity at low confidence."""
    severity = SafetyRecommender.get_severity("fire", 0.30)
    assert severity == AlertSeverity.INFO


def test_get_severity_smoke_critical():
    """Test smoke severity at critical threshold."""
    severity = SafetyRecommender.get_severity("smoke", 0.85)
    assert severity == AlertSeverity.CRITICAL


def test_get_severity_smoke_warning():
    """Test smoke severity at warning threshold."""
    severity = SafetyRecommender.get_severity("smoke", 0.50)
    assert severity == AlertSeverity.WARNING


def test_get_severity_smoke_low():
    """Test smoke severity at low confidence."""
    severity = SafetyRecommender.get_severity("smoke", 0.30)
    assert severity == AlertSeverity.INFO


def test_generate_safety_report_success():
    """Test generating safety report on successful detection."""
    detections = {
        "status": "success",
        "detections": [
            {"class": "fire", "confidence": 0.92},
            {"class": "smoke", "confidence": 0.78}
        ],
        "alerts": [
            {
                "type": "fire",
                "message": "Critical Fire Hazard Detected",
                "confidence": 0.92,
                "severity": "CRITICAL"
            },
            {
                "type": "smoke",
                "message": "Potential Smoke Hazard Detected",
                "confidence": 0.78,
                "severity": "WARNING"
            }
        ]
    }
    
    report = SafetyRecommender.generate_safety_report(detections)
    
    assert report["status"] == "success"
    assert "CRITICAL" in report["overall_status"]
    assert len(report["critical_alerts"]) > 0
    assert len(report["warning_alerts"]) > 0
    assert len(report["recommendations"]) > 0


def test_generate_safety_report_no_alerts():
    """Test generating safety report with no alerts."""
    detections = {
        "status": "success",
        "detections": [],
        "alerts": []
    }
    
    report = SafetyRecommender.generate_safety_report(detections)
    
    assert report["status"] == "success"
    assert "SAFE" in report["overall_status"]
    assert len(report["critical_alerts"]) == 0
    assert len(report["warning_alerts"]) == 0


def test_generate_safety_report_failed():
    """Test generating safety report on failed detection."""
    detections = {
        "status": "failed",
        "error": "Test error"
    }
    
    report = SafetyRecommender.generate_safety_report(detections)
    
    assert report["status"] == "failed"
    assert report["error"] == "Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
