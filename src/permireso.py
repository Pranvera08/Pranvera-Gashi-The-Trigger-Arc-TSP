"""
Post-optimizimi ("përmirëso"): ILS i nisur nga zgjidhja më e mirë e njohur.

Për çdo instancë:
  1. lexohen të gjitha zgjidhjet që ekzistojnë (sa, grasp, ils, sa_v1 dhe
     rekordi i mëparshëm i këtij hapi), kontrollohen dhe merret më e mira;
  2. raund: ILS nga ajo zgjidhje me disa seed-e paralelisht, secili për `koha` s;
  3. nëse u gjet rekord i ri, raundi tjetër nis prej tij; përndryshe ndalet;
  4. rekordet ruhen te results/me_te_mirat_e_njohura/.

Ky hap NUK i prek rezultatet e results/sa, grasp, ils, që krahasimi i
algoritmeve (kohë e barabartë, e njëjta pikënisje) të mbetet i drejtë.
"""
import csv
import multiprocessing as mp
import time
from datetime import datetime
from pathlib import Path

from ils import iterated_local_search
from instanca import ngarko
from kosto import llogarit_koston

# Instanca e ngarkuar në çdo proces
_KTX = None
_SKEDARI = None


def _pergatit(skedari):
    global _KTX, _SKEDARI
    if _SKEDARI != skedari:
        _KTX = ngarko(skedari)
        _SKEDARI = skedari


def _nje_prove(detyra):
    skedari, rruga, seed, koha = detyra
    _pergatit(skedari)
    rez = iterated_local_search(_KTX, rruga, seed=seed, koha_max=koha)
    kontrolli = llogarit_koston(_KTX, rez["rruga"])
    if abs(kontrolli - rez["kosto"]) > 1e-6:
        raise RuntimeError(f"Kostoja nuk përputhet: {kontrolli} != {rez['kosto']}")
    return rez["kosto"], rez["rruga"], seed


def _lexo_rrugen(skedari):
    return [int(v) for v in Path(skedari).read_text(encoding="utf-8").split()]


def gjej_pikenisjen(ktx, emri, rezultatet):
    """Kthen (rruga, kosto, burimi) për zgjidhjen më të mirë të vlefshme që ekziston."""
    kandidatet = [
        (rezultatet / "me_te_mirat_e_njohura" / f"{emri}.txt", "rekordi i mëparshëm"),
        (rezultatet / "sa" / "zgjidhjet" / f"{emri}.txt", "sa"),
        (rezultatet / "grasp" / "zgjidhjet" / f"{emri}.txt", "grasp"),
        (rezultatet / "ils" / "zgjidhjet" / f"{emri}.txt", "ils"),
        (rezultatet / "sa_v1" / f"{emri}_zgjidhja.txt", "sa_v1"),
    ]
    me_e_mira = None
    for skedari, burimi in kandidatet:
        if not skedari.exists():
            continue
        try:
            rruga = _lexo_rrugen(skedari)
            kosto = llogarit_koston(ktx, rruga)
        except (ValueError, OSError):
            continue                       # skedar i dëmtuar ose rrugë e pavlefshme
        if me_e_mira is None or kosto < me_e_mira[1] - 1e-9:
            me_e_mira = (rruga, kosto, burimi)
    return me_e_mira


def _raunde_te_meparshme(historia, emri):
    if not historia.exists():
        return 0
    with open(historia, encoding="utf-8") as f:
        return sum(1 for r in csv.DictReader(f) if r["instanca"] == emri)


def permireso_instancen(emri, instancat, rezultatet, koha, raunde, procese):
    dosja = rezultatet / "me_te_mirat_e_njohura"
    dosja.mkdir(parents=True, exist_ok=True)
    historia = dosja / "historia.csv"
    skedari = str(instancat / f"{emri}.txt")

    _pergatit(skedari)
    ktx = _KTX
    fillimi = gjej_pikenisjen(ktx, emri, rezultatet)
    if fillimi is None:
        print(f"\n=== {emri}: nuk ka asnjë zgjidhje për të nisur; ekzekuto fillimisht algoritmet.")
        return
    rruga, kosto, burimi = fillimi
    print(f"\n=== {emri}: n={ktx.n}, pikënisja {kosto:.2f} (nga {burimi})")

    baza = _raunde_te_meparshme(historia, emri)   # seed-e të reja në çdo ekzekutim
    for raundi in range(1, raunde + 1):
        seeds = [1000 * (baza + raundi) + k for k in range(procese)]
        detyrat = [(skedari, rruga, s, koha) for s in seeds]
        t0 = time.perf_counter()
        if procese > 1:
            with mp.Pool(processes=procese, initializer=_pergatit, initargs=(skedari,)) as pool:
                rezultatet_raundit = pool.map(_nje_prove, detyrat)
        else:
            rezultatet_raundit = [_nje_prove(d) for d in detyrat]
        k_re, rruga_re, seed_i_mire = min(rezultatet_raundit, key=lambda x: x[0])
        u_permiresua = k_re < kosto - 1e-9

        rreshti = {
            "instanca": emri, "raundi": baza + raundi, "burimi": burimi,
            "kosto_para": f"{kosto:.2f}", "kosto_pas": f"{min(k_re, kosto):.2f}",
            "u_permiresua": "po" if u_permiresua else "jo", "seed_i_mire": seed_i_mire,
            "seed_e": len(seeds), "koha_max": koha,
            "sekonda": f"{time.perf_counter() - t0:.1f}",
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        ka_koke = historia.exists() and historia.stat().st_size > 0
        with open(historia, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rreshti.keys()))
            if not ka_koke:
                w.writeheader()
            w.writerow(rreshti)

        if u_permiresua:
            print(f"  raundi {raundi}: {kosto:.2f} -> {k_re:.2f}  (rekord i ri)")
            rruga, kosto, burimi = rruga_re, k_re, "rekordi i mëparshëm"
        else:
            print(f"  raundi {raundi}: {kosto:.2f} -> pa përmirësim, ndalet")

        # ruhet gjithmonë zgjidhja më e mirë e njohur (e kontrolluar)
        llogarit_koston(ktx, rruga)
        (dosja / f"{emri}.txt").write_text(" ".join(map(str, rruga)) + "\n", encoding="utf-8")

        if not u_permiresua:
            break


def _rendit(emri):
    pjesa = emri[3:] if emri.startswith("grf") else ""
    return (0, int(pjesa)) if pjesa.isdigit() else (1, emri)


def perditeso_permbledhjen(rezultatet):
    """permbledhja.csv: për çdo instancë më e mira e algoritmeve dhe rekordi."""
    dosja = rezultatet / "me_te_mirat_e_njohura"
    historia = dosja / "historia.csv"
    if not historia.exists():
        return
    with open(historia, encoding="utf-8") as f:
        rreshtat = list(csv.DictReader(f))

    sipas = {}
    for r in rreshtat:
        sipas.setdefault(r["instanca"], []).append(r)

    dalja = []
    for emri in sorted(sipas, key=_rendit):
        lista = sorted(sipas[emri], key=lambda r: int(r["raundi"]))
        para = float(lista[0]["kosto_para"])
        pas = min(float(r["kosto_pas"]) for r in lista)
        dalja.append({
            "instanca": emri,
            "me_e_mira_para": f"{para:.2f}",
            "burimi": lista[0]["burimi"],
            "rekordi": f"{pas:.2f}",
            "permiresimi_%": f"{(para - pas) / para * 100:.2f}",
            "raunde": len(lista),
            "raunde_me_permiresim": sum(r["u_permiresua"] == "po" for r in lista),
        })

    with open(dosja / "permbledhja.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dalja[0].keys()))
        w.writeheader()
        w.writerows(dalja)