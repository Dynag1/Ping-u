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
    OFFLINE = "#4d4d4d"    # Timeout / HS (gris foncé)
    
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
        """
        Retourne la couleur hexadécimale correspondant à la latence.
        
        Règles:
        - < 50ms : vert pâle
        - 50ms à 100ms : orange pâle
        - > 100ms : rouge pâle
        - >= 500ms (HS) : gris foncé
        """
        if latency_ms >= 500:
            # Hors service (HS)
            return cls.NOIR_GRIS
        elif latency_ms > 100:
            # Rouge pâle pour latence > 100ms
            return cls.ROUGE_PALE
        elif latency_ms >= 50:
            # Orange pâle pour latence entre 50ms et 100ms
            return cls.ORANGE_PALE
        else:
            # Vert pâle pour latence < 50ms
            return cls.VERT_PALE
