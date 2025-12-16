"""Analytics widget combining Cost tracking and Performance analysis."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
)
from PyQt6.QtCore import Qt

from .cost_widget import CostWidget
from .analysis_widget import AnalysisWidget


class AnalyticsWidget(QWidget):
    """Combined analytics widget with Cost and Performance tabs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Cost tab
        self.cost_widget = CostWidget()
        self.tabs.addTab(self.cost_widget, "💰 Cost")

        # Performance tab
        self.performance_widget = AnalysisWidget()
        self.tabs.addTab(self.performance_widget, "📊 Performance")

        layout.addWidget(self.tabs)

    def refresh(self):
        """Refresh all analytics data."""
        # Refresh both sub-widgets
        if hasattr(self.cost_widget, 'refresh'):
            self.cost_widget.refresh()
        if hasattr(self.performance_widget, 'refresh'):
            self.performance_widget.refresh()

    def force_refresh(self):
        """Force refresh (bypass cache)."""
        if hasattr(self.cost_widget, 'force_refresh'):
            self.cost_widget.force_refresh()
        if hasattr(self.performance_widget, 'refresh'):
            self.performance_widget.refresh()
