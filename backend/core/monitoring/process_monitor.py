"""Sistema de Monitoreo de Procesos con principios SOLID y patrones de diseño."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol, Any, Callable
from collections import defaultdict
import json
import statistics


class ProcessStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ProcessMetric:
    process_id: str
    process_name: str
    status: ProcessStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.end_time and self.start_time:
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000


class IMetricCollector(Protocol):
    def collect(self, metric: ProcessMetric) -> None: ...
    def get_metrics(self, process_id: str) -> List[ProcessMetric]: ...


class IReliabilityCalculator(Protocol):
    def calculate(self, metrics: List[ProcessMetric]) -> float: ...


class IReportGenerator(Protocol):
    def generate(
        self,
        metrics: Dict[str, List[ProcessMetric]],
        calculator: Optional[IReliabilityCalculator] = None,
    ) -> str: ...


class IProcessObserver(Protocol):
    def on_process_start(self, process_id: str, metadata: Dict[str, Any]) -> None: ...
    def on_process_end(
        self, process_id: str, status: ProcessStatus, error: Optional[str] = None
    ) -> None: ...


# ============================================================================
# ESTRATEGIAS (Patrón Strategy)
# ============================================================================


class ReliabilityStrategy(ABC):
    @abstractmethod
    def calculate(self, metrics: List[ProcessMetric]) -> float:
        pass


class SuccessRateStrategy(ReliabilityStrategy):
    def calculate(self, metrics: List[ProcessMetric]) -> float:
        if not metrics:
            return 0.0
        successful = sum(1 for m in metrics if m.status == ProcessStatus.SUCCESS)
        return (successful / len(metrics)) * 100


# ============================================================================
# RECOLECTOR (SRP)
# ============================================================================


class MetricCollector:
    def __init__(self):
        self._metrics: Dict[str, List[ProcessMetric]] = defaultdict(list)

    def start_process(
        self,
        process_id: str,
        process_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metric = ProcessMetric(
            process_id=process_id,
            process_name=process_name,
            status=ProcessStatus.RUNNING,
            start_time=datetime.now(),
            metadata=metadata or {},
        )
        self._metrics[process_id].append(metric)

    def end_process(
        self, process_id: str, status: ProcessStatus, error: Optional[str] = None
    ) -> None:
        if process_id in self._metrics and self._metrics[process_id]:
            last = self._metrics[process_id][-1]
            if last.status == ProcessStatus.RUNNING:
                last.status = status
                last.end_time = datetime.now()
                last.error_message = error

    def get_metrics(self, process_id: str) -> List[ProcessMetric]:
        return self._metrics.get(process_id, [])

    def get_all_metrics(self) -> Dict[str, List[ProcessMetric]]:
        return dict(self._metrics)


# ============================================================================
# OBSERVADOR (Patrón Observer)
# ============================================================================


class ProcessObserver:
    def __init__(self):
        self._start_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self._end_callbacks: List[
            Callable[[str, ProcessStatus, Optional[str]], None]
        ] = []

    def subscribe_start(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        self._start_callbacks.append(callback)

    def subscribe_end(
        self, callback: Callable[[str, ProcessStatus, Optional[str]], None]
    ) -> None:
        self._end_callbacks.append(callback)

    def notify_start(self, process_id: str, metadata: Dict[str, Any]) -> None:
        for cb in self._start_callbacks:
            cb(process_id, metadata)

    def notify_end(
        self, process_id: str, status: ProcessStatus, error: Optional[str] = None
    ) -> None:
        for cb in self._end_callbacks:
            cb(process_id, status, error)


# ============================================================================
# FÁBRICA (Patrón Factory)
# ============================================================================


class MetricFactory:
    @staticmethod
    def create_reliability_calculator(
        strategy: str = "success_rate",
    ) -> ReliabilityStrategy:
        if strategy == "success_rate":
            return SuccessRateStrategy()
        raise ValueError(f"Estrategia no soportada: {strategy}")

    @staticmethod
    def create_report_generator(fmt: str = "text") -> "IReportGenerator":
        if fmt == "text":
            return TextReportGenerator()
        elif fmt == "json":
            return JsonReportGenerator()
        raise ValueError(f"Formato no soportado: {fmt}")


# ============================================================================
# GENERADORES DE REPORTES
# ============================================================================


class TextReportGenerator:
    def generate(
        self,
        metrics: Dict[str, List[ProcessMetric]],
        calculator: Optional[IReliabilityCalculator] = None,
    ) -> str:
        lines = ["=" * 60, "REPORTE DE MONITOREO", "=" * 60]
        for pid, pm in metrics.items():
            ok = sum(1 for m in pm if m.status == ProcessStatus.SUCCESS)
            lines.append(f"{pid}: {ok}/{len(pm)} exitosos")
        return "\n".join(lines)


class JsonReportGenerator:
    def generate(
        self,
        metrics: Dict[str, List[ProcessMetric]],
        calculator: Optional[IReliabilityCalculator] = None,
    ) -> str:
        data = {}
        for pid, pm in metrics.items():
            ok = sum(1 for m in pm if m.status == ProcessStatus.SUCCESS)
            data[pid] = {"total": len(pm), "success": ok}
        return json.dumps(data, indent=2)


# ============================================================================
# MONITOR PRINCIPAL (DIP)
# ============================================================================


class ProcessMonitor:
    def __init__(
        self,
        collector: Optional[MetricCollector] = None,
        observer: Optional[ProcessObserver] = None,
        strategy: str = "success_rate",
    ):
        self._collector = collector or MetricCollector()
        self._observer = observer or ProcessObserver()
        self._calc = MetricFactory.create_reliability_calculator(strategy)
        self._observer.subscribe_start(
            lambda pid, m: self._collector.start_process(pid, pid, m)
        )
        self._observer.subscribe_end(
            lambda pid, s, e: self._collector.end_process(pid, s, e)
        )

    def track_process(
        self,
        process_id: str,
        process_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        return _ProcessTracker(self, process_id, process_name, metadata)

    def get_reliability(self, process_id: str) -> float:
        return self._calc.calculate(self._collector.get_metrics(process_id))

    def get_all_reliabilities(self) -> Dict[str, float]:
        return {
            pid: self.get_reliability(pid) for pid in self._collector.get_all_metrics()
        }

    def generate_report(self, fmt: str = "text") -> str:
        gen = MetricFactory.create_report_generator(fmt)
        return gen.generate(self._collector.get_all_metrics(), self._calc)


class _ProcessTracker:
    def __init__(
        self,
        monitor: ProcessMonitor,
        process_id: str,
        process_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self._monitor = monitor
        self._pid = process_id
        self._name = process_name
        self._meta = metadata or {}

    def __enter__(self):
        self._monitor._observer.notify_start(self._pid, self._meta)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._monitor._observer.notify_end(self._pid, ProcessStatus.SUCCESS)
        else:
            self._monitor._observer.notify_end(
                self._pid, ProcessStatus.FAILED, str(exc_val) if exc_val else None
            )
        return False


_global_monitor: Optional[ProcessMonitor] = None


def get_monitor() -> ProcessMonitor:
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ProcessMonitor()
    return _global_monitor


def track(
    process_id: str, process_name: str, metadata: Optional[Dict[str, Any]] = None
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with get_monitor().track_process(process_id, process_name, metadata):
                return func(*args, **kwargs)

        return wrapper

    return decorator
