from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)

    @property
    def is_technique(self) -> bool:
        category = self.metadata.get("practice_category", "")
        return category in ("pranayama", "asana", "meditation", "dharana", "mantra")


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, full_text: str, source_metadata: dict) -> list[Chunk]:
        """Split text into semantically meaningful chunks."""
        ...

    def _classify_practice_category(self, text: str) -> str:
        """Classify a chunk's practice category based on keyword presence."""
        text_lower = text.lower()

        pranayama_keywords = [
            "pranayama", "breath", "inhale", "exhale", "kumbhaka", "rechaka",
            "puraka", "nadi shodhana", "kapalabhati", "bhastrika", "ujjayi",
            "sitali", "sitkari", "bhramari", "surya bhedana",
        ]
        asana_keywords = [
            "asana", "posture", "pose", "padmasana", "siddhasana", "vajrasana",
            "matsyasana", "halasana", "bhujangasana", "sarvangasana", "sirsasana",
            "trikonasana", "virabhadrasana", "shavasana",
        ]
        meditation_keywords = [
            "meditation", "dharana", "dhyana", "concentration", "contemplate",
            "visualize", "focus the mind", "one-pointedness", "samadhi",
            "trataka", "mantra", "japa",
        ]

        scores = {
            "pranayama": sum(1 for k in pranayama_keywords if k in text_lower),
            "asana": sum(1 for k in asana_keywords if k in text_lower),
            "meditation": sum(1 for k in meditation_keywords if k in text_lower),
        }

        max_category = max(scores, key=scores.get)
        if scores[max_category] >= 2:
            return max_category
        if scores[max_category] == 1:
            return max_category

        return "philosophy"
