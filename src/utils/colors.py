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
    VERT_PALE = "#baf595"   # Vert clair pour IP OK
    JAUNE_PALE = "#fffd6a"
    ORANGE_PALE = "#ffb845"
    ROUGE_PALE = "#f97e7e"  # Rouge pour IP DOWN
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
        - < 100ms : vert clair
        - 100ms à 200ms : jaune clair
        - > 200ms (mais < 500ms) : orange clair
        - >= 500ms (HS) : rouge (IP DOWN)
        """
        if latency_ms >= 500:
            # Hors service (HS) - rouge pour IP DOWN
            return cls.ROUGE_PALE
        elif latency_ms > 200:
            # Latence élevée - orange clair
            return cls.ORANGE_PALE
        elif latency_ms >= 100:
            # Latence moyenne - jaune clair
            return cls.JAUNE_PALE
        else:
            # Latence faible (< 100ms) - vert clair
            return cls.VERT_PALE


def format_bandwidth(value_mbps: float) -> str:
    """
    Formate automatiquement le débit avec l'unité appropriée.
    
    Args:
        value_mbps: Valeur en Mbps (Megabits par seconde)
    
    Returns:
        Chaîne formatée avec l'unité appropriée (bps, Kbps, Mbps, Gbps)
    
    Examples:
        >>> format_bandwidth(0.0005)
        '500 bps'
        >>> format_bandwidth(0.5)
        '500 Kbps'
        >>> format_bandwidth(50)
        '50 Mbps'
        >>> format_bandwidth(1500)
        '1.5 Gbps'
    """
    if value_mbps is None or value_mbps < 0:
        return '-'
    
    # Seuil pour considérer comme 0 (< 0.1 bps = activité réseau insignifiante)
    if value_mbps < 0.0000001:  # < 0.1 bps
        return '-'
    
    # Convertir Mbps en bps pour calculer l'unité appropriée
    bps = value_mbps * 1_000_000
    
    if bps >= 1_000_000_000:
        # Gbps (Gigabits par seconde)
        return f"{bps / 1_000_000_000:.2f} Gbps"
    elif bps >= 1_000_000:
        # Mbps (Megabits par seconde)
        return f"{bps / 1_000_000:.2f} Mbps"
    elif bps >= 1_000:
        # Kbps (Kilobits par seconde)
        return f"{bps / 1_000:.2f} Kbps"
    elif bps >= 1:
        # bps (bits par seconde) - afficher avec 1 décimale
        return f"{bps:.1f} bps"
    else:
        # Très petites valeurs (< 1 bps mais > 0.1 bps)
        return f"{bps:.2f} bps"
