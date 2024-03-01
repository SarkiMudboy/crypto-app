from abc import abstractmethod
from abc import ABC
from typing import Dict, Any

class Handler(ABC):
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        pass