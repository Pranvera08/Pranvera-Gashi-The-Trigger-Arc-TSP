"""
Leximi i instancës dhe përgatitja e strukturave që i përdorin të gjitha algoritmet.
"""
from dataclasses import dataclass

import math
from array import array


@dataclass
class Harku:
    id: int
    prej: int
    deri: int
    kosto: float


def lexo_instancen(emri_skedarit):
    """
    Lexon nyjet, harqet dhe marrëdhëniet trigger nga skedari.

    Disa instanca (p.sh. grf15) kanë miliona marrëdhënie. Nëse secila
    ruhet si fjalor më vete, programi zë disa GB memorie dhe bëhet
    shumë i ngadalshëm. Prandaj marrëdhëniet ruhen në një tabelë kompakte:
    tabela[i_trigger * m + i_objektiv] = kosto e re
    ku i_trigger dhe i_objektiv janë pozitat e harqeve (0 .. m-1).
    Vlera NaN do të thotë që marrëdhënia nuk ekziston.
    """
    with open(emri_skedarit, "r", encoding="utf-8") as skedari:
        rreshtat = (
            rreshti.split()
            for rreshti in skedari
            if rreshti.strip() and not rreshti.lstrip().startswith("#")
        )

        try:
            koka = next(rreshtat)
        except StopIteration:
            raise ValueError("Skedari i instancës është bosh.")

        # Rreshti i parë: numri i nyjeve, harqeve dhe marrëdhënieve
        n, m, r = int(koka[0]), int(koka[1]), int(koka[2])

        harqet = {}

        # Rreshtat e harqeve: id, nyja prej, nyja deri, kostoja
        for _ in range(m):
            id_harku, prej, deri, kosto = next(rreshtat)
            id_harku = int(id_harku)
            harqet[id_harku] = Harku(
                id_harku, int(prej), int(deri), float(kosto)
            )

        # Pozita e çdo harku në tabelë (0 .. m-1)
        pozita_e_harkut = {
            id_harku: i for i, id_harku in enumerate(harqet)
        }

        tabela = array("d", [math.nan]) * (m * m)
        numri = 0

        # Rreshtat e marrëdhënieve trigger:
        # id, (id, prej, deri) e trigger-it, (id, prej, deri) e objektivit,
        # kosto e re. Na duhen vetëm id-të e harqeve dhe kostoja.
        for _ in range(r):
            rr = next(rreshtat)
            i_trigger = pozita_e_harkut[int(rr[1])]
            i_objektiv = pozita_e_harkut[int(rr[4])]
            tabela[i_trigger * m + i_objektiv] = float(rr[7])
            numri += 1

    marredheniet = {
        "tabela": tabela,
        "pozita_e_harkut": pozita_e_harkut,
        "numri": numri,
    }

    return n, harqet, marredheniet


def pergatit_indekset(harqet, marredheniet):
    """
    Përgatit hartat që përdoren gjatë kërkimit.
    Këto harta përgatiten një herë dhe ripërdoren.
    """
    pozita_e_harkut = marredheniet["pozita_e_harkut"]

    # (prej, deri) -> pozita e harkut në tabelë
    harku_sipas_nyjeve = {
        (harku.prej, harku.deri): pozita_e_harkut[id_harku]
        for id_harku, harku in harqet.items()
    }

    # kosto fillestare sipas pozitës së harkut
    kostot_baze = [0.0] * len(harqet)
    for id_harku, harku in harqet.items():
        kostot_baze[pozita_e_harkut[id_harku]] = harku.kosto

    return harku_sipas_nyjeve, kostot_baze


class Konteksti:
    """
    Të gjitha të dhënat e instancës që u duhen algoritmeve, të përgatitura një herë.

    hs[(prej, deri)]  -> pozita e harkut (0 .. m-1)
    kostot_baze[i]    -> kostoja fillestare e harkut i
    tabela[t*m + a]   -> kostoja e re e harkut a kur trigger-i i fundit është t (NaN = s'ka)
    fqinjet[u]        -> nyjet ku mund të shkohet nga u
    """

    def __init__(self, n, harqet, marredheniet):
        self.n = n
        self.harqet = harqet
        self.marredheniet = marredheniet
        self.tabela = marredheniet["tabela"]
        self.hs, self.kostot_baze = pergatit_indekset(harqet, marredheniet)
        self.m = len(self.kostot_baze)
        self.fqinjet = [[] for _ in range(n)]
        for (prej, deri) in self.hs:
            self.fqinjet[prej].append(deri)
        self.kosto_mesatare = sum(self.kostot_baze) / self.m


def ngarko(skedari):
    """Lexon instancën dhe kthen kontekstin e gatshëm."""
    n, harqet, marredheniet = lexo_instancen(skedari)
    return Konteksti(n, harqet, marredheniet)
