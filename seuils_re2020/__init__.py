"""
seuils_re2020 — calcul des seuils réglementaires de la RE2020.

Exemple :
    from seuils_re2020 import Projet, calculer
    r = calculer(Projet(usage_id=2, zone="H1a", altitude="<400m", sref=3000,
                        periode_pc="2028 à 2030", nb_logements=50))
    r["bbio_max"].valeur
"""
from .calculs import Resultat, calculer
from .controles import alertes
from .regles import Projet, decret_2026_applicable, decret_applicable
from .travaux import Regime, regime_travaux
from .variables import VERSION

__version__ = VERSION
__all__ = ["Projet", "Resultat", "calculer", "alertes", "decret_2026_applicable", "decret_applicable",
           "Regime", "regime_travaux", "__version__"]
