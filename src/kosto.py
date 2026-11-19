"""
Llogaritja e kostos së një rruge me trigger-a.

Rregulli: kostoja e harkut a është kostoja nga trigger-i i FUNDIT që është
kaluar para a. Nëse asnjë trigger i a nuk është kaluar, merret kostoja bazë.

Dy ide e bëjnë llogaritjen më të shpejtë gjatë kërkimit:

1. Vlerësimi i pjesshëm. Nëse rruga kandidate ndryshon vetëm nga harku s e
   tutje, harqet 0 .. s-1 kanë të njëjtët paraardhës, pra edhe të njëjtën
   kosto. Ato nuk rillogariten: merret shuma e tyre e ruajtur (prefiksi).

2. Ndërprerja e hershme. Të gjitha kostot në instanca janë >= 0, prandaj
   shuma vetëm rritet. Sapo shuma e pjesshme e kalon kufirin (p.sh. koston
   aktuale te kërkimi lokal), kandidati refuzohet pa e mbaruar llogaritjen.
"""
import math


class Gjendja:
    """
    Një rrugë bashkë me të dhënat e ruajtura për vlerësim të shpejtë.

    nyjet[k]    -> nyja në pozitën k (nyjet[0] = nyjet[n] = 0)
    harqet[k]   -> pozita e harkut (nyjet[k], nyjet[k+1])
    rreshtat[k] -> harqet[k] * m (rreshti i harkut në tabelë)
    kostot[k]   -> kostoja e harkut k në këtë rrugë
    prefiksi[k] -> shuma e kostot[0 .. k-1]
    """

    def __init__(self, ktx, nyjet):
        self.nyjet = list(nyjet)
        rezultati = vlereso_nga(ktx, self, self.nyjet, 0, bosh=True)
        self._vendos(*rezultati)

    def _vendos(self, kosto, harqet, rreshtat, kostot):
        self.kosto = kosto
        self.harqet = harqet
        self.rreshtat = rreshtat
        self.kostot = kostot
        prefiksi = [0.0]
        for c in kostot:
            prefiksi.append(prefiksi[-1] + c)
        self.prefiksi = prefiksi

    def prano(self, nyjet, rezultati):
        """Kalon te rruga kandidate, duke ripërdorur rezultatin e vlerësimit."""
        self.nyjet = nyjet
        self._vendos(*rezultati)

    def kopje(self):
        g = object.__new__(Gjendja)
        g.nyjet = self.nyjet[:]
        g.kosto = self.kosto
        g.harqet = self.harqet[:]
        g.rreshtat = self.rreshtat[:]
        g.kostot = self.kostot[:]
        g.prefiksi = self.prefiksi[:]
        return g


def vlereso_nga(ktx, gjendja, nyjet, s, kufiri=math.inf, bosh=False):
    """
    Llogarit koston e rrugës 'nyjet', duke supozuar që harqet 0 .. s-1 janë
    të njëjta me ato të 'gjendja'. Harqet e reja duhet të ekzistojnë
    (lëvizjet i kontrollojnë para se të thirret ky funksion).

    Kthen (kosto, harqet, rreshtat, kostot) ose None nëse kosto >= kufiri.
    """
    hs = ktx.hs
    tabela = ktx.tabela
    baze = ktx.kostot_baze
    m = ktx.m

    if bosh:
        harqet, rreshtat, kostot, totali = [], [], [], 0.0
    else:
        harqet = gjendja.harqet[:s]
        rreshtat = gjendja.rreshtat[:s]
        kostot = gjendja.kostot[:s]
        totali = gjendja.prefiksi[s]

    for p in range(s, len(nyjet) - 1):
        j = hs[(nyjet[p], nyjet[p + 1])]
        c = baze[j]

        # trigger-i i fundit para pozitës p
        for k in range(p - 1, -1, -1):
            v = tabela[rreshtat[k] + j]
            if v == v:          # NaN != NaN, pra këtu ka marrëdhënie
                c = v
                break

        harqet.append(j)
        rreshtat.append(j * m)
        kostot.append(c)
        totali += c

        if totali >= kufiri:
            return None

    return totali, harqet, rreshtat, kostot


def kontrollo_rrugen(ktx, nyjet):
    """Kontroll i plotë: cikël Hamiltonian nga 0 me harqe që ekzistojnë."""
    n = ktx.n
    if len(nyjet) != n + 1 or nyjet[0] != 0 or nyjet[-1] != 0:
        raise ValueError("Rruga duhet të nisë e të mbarojë te 0 dhe të ketë n + 1 nyje.")
    if set(nyjet[:-1]) != set(range(n)):
        raise ValueError("Rruga nuk është cikël Hamiltonian.")
    for prej, deri in zip(nyjet, nyjet[1:]):
        if (prej, deri) not in ktx.hs:
            raise ValueError(f"Nuk ekziston harku nga {prej} te {deri}.")


def llogarit_koston(ktx, nyjet):
    """Kostoja e plotë e një rruge, me kontroll të vlefshmërisë."""
    kontrollo_rrugen(ktx, nyjet)
    return vlereso_nga(ktx, None, nyjet, 0, bosh=True)[0]
