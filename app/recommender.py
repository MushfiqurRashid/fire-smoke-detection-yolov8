"""
Recommendation engine for safety actions based on fire and smoke detection.

Generates automated recommendations and safety alerts.
"""

from typing import Dict, List, Optional
from enum import Enum
import logging

from src.logger import setup_logger

logger = setup_logger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SafetyRecommender:
    """Generate safety recommendations based on detections."""

    # Recommendation templates
    RECOMMENDATIONS = {
        "fire": [
            "Trigger emergency response and inspect the affected area immediately.",
            "Evacuate the area if safe to do so.",
            "Contact emergency services (911 or local emergency number).",
            "Do not attempt to extinguish large fires yourself.",
            "Use fire extinguishers only for small, contained fires."
        ],
        "smoke": [
            "Investigate the source of smoke and check for overheating equipment.",
            "Ensure proper ventilation in the affected area.",
            "Check for electrical fires or equipment malfunctions.",
            "Monitor the situation closely and be prepared to evacuate.",
            "Use a thermal camera to locate the source of the smoke."
        ]
    }

    SEVERITY_RULES = {
        "fire": {
            0.85: AlertSeverity.CRITICAL,
            0.60: AlertSeverity.CRITICAL,
        },
        "smoke": {
            0.85: AlertSeverity.CRITICAL,
            0.50: AlertSeverity.WARNING,
        }
    }

    @staticmethod
    def get_recommendations(detection_type: str) -> List[str]:
        """
        Get safety recommendations for a detection type.

        Args:
            detection_type: Type of detection ('fire' or 'smoke')

        Returns:
            List of safety recommendations
        """
        return SafetyRecommender.RECOMMENDATIONS.get(detection_type, [])

    @staticmethod
    def get_severity(detection_type: str, confidence: float) -> AlertSeverity:
        """
        Determine alert severity based on detection type and confidence.

        Args:
            detection_type: Type of detection ('fire' or 'smoke')
            confidence: Confidence score (0-1)

        Returns:
            Alert severity level
        """
        if detection_type not in SafetyRecommender.SEVERITY_RULES:
            return AlertSeverity.INFO

        rules = SafetyRecommender.SEVERITY_RULES[detection_type]
        
        # Check rules in descending order of confidence threshold
        for threshold, severity in sorted(rules.items(), reverse=True):
            if confidence >= threshold:
                return severity

        return AlertSeverity.INFO

    @staticmethod
    def generate_safety_report(detections: Dict) -> Dict:
        """
        Generate comprehensive safety report from detections.

        Args:
            detections: Detection results from predictor

        Returns:
            Safety report with recommendations
        """
        if detections.get("status") != "success":
            return {
                "status": "failed",
                "error": detections.get("error", "Unknown error"),
                "recommendations": []
            }

        alerts = detections.get("alerts", [])
        all_recommendations = set()
        critical_alerts = []
        warning_alerts = []

        for alert in alerts:
            alert_type = alert.get("type")
            recommendations = SafetyRecommender.get_recommendations(alert_type)
            all_recommendations.update(recommendations)

            if alert.get("severity") == "CRITICAL":
                critical_alerts.append(alert)
            elif alert.get("severity") == "WARNING":
                warning_alerts.append(alert)

        # Determine overall safety status
        if critical_alerts:
            overall_status = "CRITICAL - IMMEDIATE ACTION REQUIRED"
        elif warning_alerts:
            overall_status = "WARNING - INVESTIGATION REQUIRED"
        elif alerts:
            overall_status = "INFO - MONITOR SITUATION"
        else:
            overall_status = "SAFE - NO THREATS DETECTED"

        return {
            "status": "success",
            "overall_status": overall_status,
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "recommendations": list(all_recommendations),
            "detection_count": len(detections.get("detections", [])),
            "alert_count": len(alerts)
        }


def main():
    """Example usage of SafetyRecommender."""
    # Example detection result
    example_detection = {
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

    report = SafetyRecommender.generate_safety_report(example_detection)
    
    print("\n" + "="*60)
    print("SAFETY REPORT")
    print("="*60)
    print(f"\nOverall Status: {report['overall_status']}")
    print(f"\nDetections: {report['detection_count']}")
    print(f"Alerts: {report['alert_count']}")
    
    if report['critical_alerts']:
        print("\n🚨 CRITICAL ALERTS:")
        for alert in report['critical_alerts']:
            print(f"  - {alert['message']} (Confidence: {alert['confidence']:.2f})")
    
    if report['warning_alerts']:
        print("\n⚠️  WARNING ALERTS:")
        for alert in report['warning_alerts']:
            print(f"  - {alert['message']} (Confidence: {alert['confidence']:.2f})")
    
    if report['recommendations']:
        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
