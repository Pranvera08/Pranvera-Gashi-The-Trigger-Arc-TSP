from dataclasses import dataclass

import math
import random

@dataclass
class Harku:
    id: int
    prej: int
    deri: int
    kosto: int


def lexo_instancen(emri_skedarit):
    """Lexon nyjet, harqet dhe marrëdhëniet trigger nga skedari."""
    with open(emri_skedarit, "r", encoding="utf-8") as skedari:
        rreshtat = []

        for rreshti in skedari:
            rreshti = rreshti.strip()

            if rreshti == "" or rreshti.startswith("#"):
                continue

            rreshtat.append([int(numri) for numri in rreshti.split()])

    if not rreshtat:
        raise ValueError("Skedari i instancës është bosh.")

    # Rreshti i parë: numri i nyjeve, harqeve dhe marrëdhënieve
    n, m, r = rreshtat[0]

    harqet = {}
    pozita = 1

    # Rreshtat e harqeve: id, nyja prej, nyja deri, kostoja
    for _ in range(m):
        id_harku, prej, deri, kosto = rreshtat[pozita]
        harqet[id_harku] = Harku(id_harku, prej, deri, kosto)
        pozita += 1

    marredheniet = []

    # Rreshtat e marrëdhënieve trigger
    for _ in range(r):
        (
            id_marredhenieje,
            id_trigger,
            trigger_prej,
            trigger_deri,
            id_objektiv,
            objektiv_prej,
            objektiv_deri,
            kosto_re,
        ) = rreshtat[pozita]

        marredheniet.append({
            "id": id_marredhenieje,
            "trigger": id_trigger,
            "trigger_prej": trigger_prej,
            "trigger_deri": trigger_deri,
            "objektiv": id_objektiv,
            "objektiv_prej": objektiv_prej,
            "objektiv_deri": objektiv_deri,
            "kosto_re": kosto_re,
        })

        pozita += 1

    return n, harqet, marredheniet


def llogarit_koston(n, harqet, marredheniet, rruga):
    """Llogarit koston e rrugës duke zbatuar trigger-at sipas rendit."""

    if len(rruga) != n + 1 or rruga[0] != 0 or rruga[-1] != 0:
        raise ValueError(
            "Rruga duhet të fillojë dhe të përfundojë te nyja 0 "
            "dhe të ketë n + 1 nyje."
        )

    # Çdo nyje duhet të vizitohet saktësisht një herë
    if set(rruga[:-1]) != set(range(n)) or len(set(rruga[:-1])) != n:
        raise ValueError("Rruga nuk është cikël Hamiltonian.")

    # Gjejmë identifikuesin e harkut nga nyja prej dhe nyja deri
    harku_sipas_nyjeve = {}

    for id_harku, harku in harqet.items():
        harku_sipas_nyjeve[(harku.prej, harku.deri)] = id_harku

    # Në fillim, secili hark e ka koston fillestare
    kostot_aktuale = {
        id_harku: harku.kosto
        for id_harku, harku in harqet.items()
    }

    # Grupojmë marrëdhëniet sipas harkut trigger
    triggerat_sipas_harkut = {}

    for marredhenia in marredheniet:
        id_trigger = marredhenia["trigger"]

        if id_trigger not in triggerat_sipas_harkut:
            triggerat_sipas_harkut[id_trigger] = []

        triggerat_sipas_harkut[id_trigger].append(marredhenia)

    harqet_e_kaluara = set()
    kosto_totale = 0

    # Kalojmë nëpër harqet e rrugës sipas rendit
    for prej, deri in zip(rruga, rruga[1:]):
        id_harku = harku_sipas_nyjeve.get((prej, deri))

        if id_harku is None:
            raise ValueError(
                f"Nuk ekziston harku nga nyja {prej} te nyja {deri}."
            )

        # Shtojmë koston aktuale të harkut
        kosto_totale += kostot_aktuale[id_harku]

        # Shënojmë se ky hark u përdor
        harqet_e_kaluara.add(id_harku)

        # Aktivizojmë trigger-at e këtij harku
        for marredhenia in triggerat_sipas_harkut.get(id_harku, []):
            id_objektiv = marredhenia["objektiv"]

            # Ndryshojmë koston vetëm nëse harku objektiv nuk është kaluar
            if id_objektiv not in harqet_e_kaluara:
                kostot_aktuale[id_objektiv] = marredhenia["kosto_re"]

    return kosto_totale


def nderto_rruge_fillestare(n, harqet):
    """Ndërton një rrugë greedy duke zgjedhur harkun më të lirë të mundshëm."""

    # Grupojmë harqet sipas nyjës prej nga nisen
    harqet_nga_nyja = {}

    for harku in harqet.values():
        if harku.prej not in harqet_nga_nyja:
            harqet_nga_nyja[harku.prej] = []

        harqet_nga_nyja[harku.prej].append(harku)

    rruga = [0]
    nyjet_papervizituara = set(range(1, n))

    while nyjet_papervizituara:
        nyja_aktuale = rruga[-1]

        kandidatet = [
            harku
            for harku in harqet_nga_nyja.get(nyja_aktuale, [])
            if harku.deri in nyjet_papervizituara
        ]

        if not kandidatet:
            raise ValueError(
                f"Nuk mund të vazhdohet nga nyja {nyja_aktuale}. "
                "Greedy nuk arriti të ndërtojë një cikël."
            )

        # Zgjedhim harkun me koston fillestare më të ulët
        harku_zgjedhur = min(kandidatet, key=lambda harku: harku.kosto)

        rruga.append(harku_zgjedhur.deri)
        nyjet_papervizituara.remove(harku_zgjedhur.deri)

    # Kontrollojmë nëse mund të kthehemi te depoja 0
    ka_hark_kthyes = any(
        harku.prej == rruga[-1] and harku.deri == 0
        for harku in harqet.values()
    )

    if not ka_hark_kthyes:
        raise ValueError(
            f"Nuk ka hark kthyes nga nyja {rruga[-1]} te depoja 0."
        )

    rruga.append(0)
    return rruga

def simulated_annealing(n, harqet, marredheniet, iteracione=10000, seed=7):
    """Përpiqet ta përmirësojë rrugën fillestare greedy."""
    gjeneratori = random.Random(seed)

    rruga_aktuale = nderto_rruge_fillestare(n, harqet)
    kosto_aktuale = llogarit_koston(
        n, harqet, marredheniet, rruga_aktuale
    )

    rruga_me_e_mire = rruga_aktuale[:]
    kosto_me_e_mire = kosto_aktuale

    temperatura = max(1.0, kosto_aktuale * 0.15)
    ftohja = 0.9995

    for _ in range(iteracione):
        # Duhet të ketë të paktën dy nyje jo-depo për t'i ndërruar
        if n <= 2:
            break

        rruga_kandidate = rruga_aktuale[:]

        # Zgjedhim dy pozita brenda rrugës dhe i ndryshojmë
        pozita_1, pozita_2 = sorted(
            gjeneratori.sample(range(1, n), 2)
        )

        if gjeneratori.random() < 0.5:
            rruga_kandidate[pozita_1], rruga_kandidate[pozita_2] = (
                rruga_kandidate[pozita_2],
                rruga_kandidate[pozita_1],
            )
        else:
            rruga_kandidate[pozita_1:pozita_2 + 1] = reversed(
                rruga_kandidate[pozita_1:pozita_2 + 1]
            )

        try:
            kosto_kandidate = llogarit_koston(
                n, harqet, marredheniet, rruga_kandidate
            )
        except ValueError:
            # Kandidati nuk ka harqet e nevojshme, prandaj e kalojmë
            temperatura *= ftohja
            continue

        ndryshimi = kosto_kandidate - kosto_aktuale

        # Pranojmë gjithmonë përmirësimet.
        # Ndonjëherë pranojmë edhe zgjidhje më të kushtueshme.
        if ndryshimi < 0 or gjeneratori.random() < math.exp(
            -ndryshimi / max(temperatura, 0.000001)
        ):
            rruga_aktuale = rruga_kandidate
            kosto_aktuale = kosto_kandidate

        if kosto_kandidate < kosto_me_e_mire:
            rruga_me_e_mire = rruga_kandidate[:]
            kosto_me_e_mire = kosto_kandidate

        temperatura *= ftohja

    return rruga_me_e_mire, kosto_me_e_mire


if __name__ == "__main__":
    # Lexojmë instancën demonstrative
    n, harqet, marredheniet = lexo_instancen("../instances/demo.txt")

    print("Numri i nyjeve:", n)
    print("Numri i harqeve:", len(harqet))
    print("Numri i marrëdhënieve:", len(marredheniet))

    rruga, kosto = simulated_annealing(
        n, harqet, marredheniet, iteracione=10000, seed=7
    )

    print("Rruga e ndërtuar:", rruga)
    print("Kostoja totale:", kosto)