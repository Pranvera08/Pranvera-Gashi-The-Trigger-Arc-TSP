from dataclasses import dataclass

import csv
import math
import random
import time
from pathlib import Path


@dataclass
class Harku:
    id: int
    prej: int
    deri: int
    kosto: float


def lexo_instancen(emri_skedarit):
    """Lexon nyjet, harqet dhe marrëdhëniet trigger nga skedari."""
    with open(emri_skedarit, "r", encoding="utf-8") as skedari:
        rreshtat = []

        for rreshti in skedari:
            rreshti = rreshti.strip()

            if rreshti == "" or rreshti.startswith("#"):
                continue

            vlera = []

            for tekst in rreshti.split():
                numer = float(tekst)

                if numer.is_integer():
                    vlera.append(int(numer))
                else:
                    vlera.append(numer)

            rreshtat.append(vlera)

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
        triggerat_sipas_harkut.setdefault(id_trigger, []).append(marredhenia)

    harqet_e_kaluara = set()
    kosto_totale = 0.0

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
    """Kërkon një cikël fillestar, duke u kthyer pas kur ngec."""

    harqet_nga_nyja = {}

    for harku in harqet.values():
        harqet_nga_nyja.setdefault(harku.prej, []).append(harku)

    lidhjet = {
        (harku.prej, harku.deri)
        for harku in harqet.values()
    }

    rruga = [0]
    nyjet_papervizituara = set(range(1, n))
    vizita = 0
    kufiri_i_kerkimit = 1_000_000

    def kerko(nyja_aktuale):
        nonlocal vizita
        vizita += 1

        if vizita > kufiri_i_kerkimit:
            return False

        if not nyjet_papervizituara:
            return (nyja_aktuale, 0) in lidhjet

        kandidatet = [
            harku
            for harku in harqet_nga_nyja.get(nyja_aktuale, [])
            if harku.deri in nyjet_papervizituara
        ]

        # Provojmë fillimisht harqet me kosto më të ulët
        kandidatet.sort(key=lambda harku: harku.kosto)

        for harku in kandidatet:
            rruga.append(harku.deri)
            nyjet_papervizituara.remove(harku.deri)

            if kerko(harku.deri):
                return True

            # Kthehemi pas dhe provojmë një hark tjetër
            nyjet_papervizituara.add(harku.deri)
            rruga.pop()

        return False

    if not kerko(0):
        raise ValueError(
            "Nuk u gjet cikël fillestar brenda kufirit të kërkimit."
        )

    rruga.append(0)
    return rruga


def simulated_annealing(n, harqet, marredheniet, iteracione=10000, seed=7):
    """Përpiqet ta përmirësojë rrugën fillestare."""
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
            temperatura *= ftohja
            continue

        ndryshimi = kosto_kandidate - kosto_aktuale

        # Pranojmë përmirësimet dhe nganjëherë edhe zgjidhje më të kushtueshme
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
    dosja_projektit = Path(__file__).resolve().parent.parent

    # Ndryshoje këtë emër kur dëshiron të provosh një instancë tjetër
    emri_instancës = "grf3"

    skedari_instancës = (
        dosja_projektit / "instances" / f"{emri_instancës}.txt"
    )
    skedari_rezultateve = (
        dosja_projektit / "results" / "results_template.csv"
    )

    # Lexojmë instancën
    n, harqet, marredheniet = lexo_instancen(skedari_instancës)

    print("Instanca:", emri_instancës)
    print("Numri i nyjeve:", n)
    print("Numri i harqeve:", len(harqet))
    print("Numri i marrëdhënieve:", len(marredheniet))

    kolonat = [
        "instance",
        "algorithm",
        "seed",
        "iterations",
        "cost",
        "seconds",
        "official_validator_valid",
    ]

    rezultatet = []

    # Gjejmë një rrugë fillestare me kërkim dhe kthim pas
    rruga_fillestare = nderto_rruge_fillestare(n, harqet)
    kosto_fillestare = llogarit_koston(
        n, harqet, marredheniet, rruga_fillestare
    )

    print("\nNdërtim me kthim pas:")
    print("Rruga:", rruga_fillestare)
    print(f"Kostoja: {kosto_fillestare:.2f}")

    rezultatet.append({
        "instance": emri_instancës,
        "algorithm": "Backtracking construction",
        "seed": 0,
        "iterations": 0,
        "cost": round(kosto_fillestare, 2),
        "seconds": "",
        "official_validator_valid": "not_checked",
    })

    # Pesë prova të Simulated Annealing, me nga 10 000 iteracione
    iteracione = 10000

    print("\nSimulated Annealing:")

    for seed in range(1, 6):
        fillimi = time.perf_counter()

        rruga, kosto = simulated_annealing(
            n,
            harqet,
            marredheniet,
            iteracione=iteracione,
            seed=seed,
        )

        koha = time.perf_counter() - fillimi

        print(
            f"Seed {seed}: rruga={rruga}, "
            f"kostoja={kosto:.2f}, koha={koha:.6f} sekonda"
        )

        rezultatet.append({
            "instance": emri_instancës,
            "algorithm": "Simulated Annealing",
            "seed": seed,
            "iterations": iteracione,
            "cost": round(kosto, 2),
            "seconds": round(koha, 6),
            "official_validator_valid": "not_checked",
        })

    # Shtojmë rezultatet në skedarin CSV
    ka_te_dhena = (
        skedari_rezultateve.exists()
        and skedari_rezultateve.stat().st_size > 0
    )

    with open(
        skedari_rezultateve,
        "a",
        newline="",
        encoding="utf-8",
    ) as skedari:
        shkruesi = csv.DictWriter(skedari, fieldnames=kolonat)

        if not ka_te_dhena:
            shkruesi.writeheader()

        shkruesi.writerows(rezultatet)

    print("\nRezultatet u ruajtën te:")
    print(skedari_rezultateve)