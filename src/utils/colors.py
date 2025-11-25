from dataclasses import dataclass

@dataclass
class AppColors:
    """
    Centralise les couleurs de l'application.
    """
    # Statuts de latence
    EXCELLENT = "#00FF00"  # < 2ms
    GOOD = "#FFFF00"       # < 10ms
    WARNING = "#FFA500"    # < 50ms
    CRITICAL = "#FF0000"   # >= 50ms
    OFFLINE = "#787878"    # Timeout / HS
    
    # Interface Utilisateur
    VERT_PALE = "#baf595"
    JAUNE_PALE = "#fffd6a"
    ORANGE_PALE = "#ffb845"
    ROUGE_PALE = "#f97e7e"
    NOIR_GRIS = "#6d6d6d"
    
    # Thème par défaut (Nord-ish)
    BG_FRAME_HAUT = "#81BEF7"
    BG_FRAME_MID = "#A9D0F5"
    BG_FRAME_DROIT = "#A9D0F5"
    BG_BUT = "#81BEF7"

    @classmethod
    def get_latency_color(cls, latency_ms: float) -> str:
        """Retourne la couleur hexadécimale correspondant à la latence."""
        if latency_ms >= 500:
            return cls.OFFLINE
        elif latency_ms < 2:
            return cls.EXCELLENT
        elif latency_ms < 10:
            return cls.GOOD
        elif latency_ms < 50:
            return cls.WARNING
        else:
            return cls.CRITICAL
