# Zgjidhja heuristike për Trigger Arc TSP

**Lënda:** Dizajni dhe Analiza e Algoritmeve  
**Studentja:** Pranvera Gashi  
**Data:** [Data e dorëzimit]  
**Kodi:** https://github.com/Pranvera08/Pranvera-Gashi-The-Trigger-Arc-TSP  
**Notebook-u në Kaggle:** [linku i notebook-ut publik]

## Përmbledhje

Ky projekt trajton Trigger Arc Travelling Salesman Problem (TA-TSP). Është një variant i problemit të shitësit udhëtues, ku kalimi nëpër një hark mund ta ndryshojë koston e një harku tjetër që kalohet më vonë. Problemi është paraqitur në konkursin MESS 2024 (Catania).

U implementuan në Python tre algoritme metaheuristike: **Simulated Annealing (SA)**, **GRASP** dhe **Iterated Local Search (ILS)**. Ato ndajnë të njëjtin funksion të kostos, të njëjtat lëvizje dhe të njëjtin kërkim lokal. Çdo algoritëm u ekzekutua në të 21 instancat e publikuara, me 5 seed-e dhe 60 sekonda për provë, në të njëjtin kompjuter (Kaggle, 4 bërthama CPU).

Rezultati kryesor: **ILS ishte algoritmi më i mirë**. Ai pati mesataren më të ulët në 11 nga 18 instancat unike, gap-in mesatar më të vogël ndaj zgjidhjes më të mirë të njohur (0.69%, kundrejt 1.35% të GRASP-it dhe 2.18% të SA-së) dhe arriti zgjidhjen më të mirë në 52% të provave. GRASP-i ishte i dyti dhe i vetmi që fitoi në instancën më të madhe, `grf15`. Krahasuar me versionin e parë të projektit (vetëm SA), kostoja më e mirë u përmirësua në 11 nga 18 instancat, deri në 6.26%.

## 1. Përshkrimi i problemit

Jepet një graf i drejtuar G = (V, A), me nyjën 0 si depo. Kërkohet një **cikël Hamiltonian** që nis te nyja 0, viziton çdo nyje saktësisht një herë dhe kthehet në 0.

Çdo hark a ka koston bazë c(a). Përveç kësaj, jepen marrëdhënie trigger r = (t, a, c'): nëse harku **t** (trigger-i) kalohet para harkut **a** (objektivi), kostoja e a bëhet c'. Rregullat janë:

1. Vlen vetëm **trigger-i i fundit** i kaluar para harkut a. Ai e fshin efektin e trigger-ave të mëparshëm.
2. Një trigger që kalohet **pas** harkut a nuk ka efekt.
3. Nëse asnjë trigger i a nuk është kaluar, merret kostoja bazë c(a).

Qëllimi është të minimizohet shuma e kostove të harqeve në cikël. Kostoja nuk varet vetëm nga cilat harqe zgjidhen, por edhe nga **rendi** i tyre. Për më tepër, grafi nuk është i plotë, prandaj jo çdo renditje e nyjeve jep cikël të vlefshëm.

## 2. Pse nuk përdoren metodat ekzakte

- **Brute force:** ka (n − 1)! rrugë. Për n = 20 kjo është rreth 1.2·10¹⁷, dhe për n = 60 numri është i paimagjinueshëm. Metoda vlen vetëm për instanca shumë të vogla.
- **Programimi dinamik (Held–Karp):** te TSP-ja klasike gjendja (bashkësia e nyjeve të vizituara, nyja e fundit) mjafton dhe jep O(n²·2ⁿ). Te TA-TSP kjo **nuk mjafton**, sepse kostoja e harqeve të ardhshëm varet nga cilat harqe janë kaluar dhe me çfarë rendi, pra nga trigger-i i fundit për çdo objektiv. Dy rrugë me të njëjtat nyje dhe të njëjtën nyje të fundit mund të kenë kosto të ndryshme për pjesën që mbetet. Gjendja duhet ta përmbajë edhe historinë e trigger-ave, dhe numri i gjendjeve rritet shumë.
- **Branch and Bound dhe ILP:** autorët e problemit kanë dhënë një model ILP (Cerrone et al.). Me miliona marrëdhënie (p.sh. `grf15` ka 4.5 milionë), modeli bëhet shumë i madh. Përveç kësaj, kufijtë e poshtëm janë të dobët, sepse trigger-at mund ta ulin koston më vonë.

Për këto arsye u zgjodhën metaheuristika, të cilat japin zgjidhje të mira brenda një kohe të kufizuar, pa garanci optimumi.

## 3. Përfaqësimi dhe llogaritja e kostos

**Zgjidhja** paraqitet si permutacion i nyjeve: `[0, v1, …, v(n−1), 0]`.

**Tabela e trigger-ave.** Gjatë leximit ndërtohet një tabelë kompakte me m × m qeliza (`array` me numra dhjetorë): qeliza `t·m + a` mban koston e re të harkut a kur trigger-i është t, ose NaN kur nuk ka marrëdhënie. Kështu kërkimi i një marrëdhënieje bëhet në O(1), edhe për instancat me miliona marrëdhënie.

**Vlerësimi.** Për çdo hark në pozitën p, kërkohet prapa nëpër harqet 0 … p−1 dhe merret trigger-i i parë që gjendet, pra ai që është kaluar i fundit. Nëse nuk ka, merret kostoja bazë.

Dy optimizime e bëjnë vlerësimin më të shpejtë gjatë kërkimit:

1. **Vlerësim i pjesshëm.** Nëse rruga kandidate ndryshon vetëm nga harku s e tutje, harqet 0 … s−1 kanë të njëjtët paraardhës, pra edhe të njëjtën kosto. Ruhet shuma e tyre (prefiksi) dhe rillogariten vetëm harqet nga s e tutje.
2. **Ndërprerje e hershme.** Të gjitha kostot në instanca janë ≥ 0, prandaj shuma vetëm rritet. Sapo shuma e pjesshme e kalon kufirin (kostoja aktuale te kërkimi lokal, ose pragu i pranimit te SA), kandidati refuzohet pa e mbaruar llogaritjen.

Çdo zgjidhje përfundimtare kontrollohet me një vlerësim të plotë: cikël Hamiltonian, harqe që ekzistojnë, kosto e rillogaritur. Pas eksperimenteve, zgjidhjet u verifikuan edhe me një vlerësues të pavarur me qasje tjetër (fjalor i trigger-ave aktivë gjatë kalimit). Të 57 zgjidhjet e kontrollueshme përputhen saktësisht. `grf15`/`grf16` nuk janë në repo, prandaj atyre iu kontrollua vetëm vlefshmëria e ciklit.

## 4. Algoritmet

### 4.1 Ndërtimi fillestar me kthim pas (backtracking)

Ndërtimi nis te nyja 0 dhe në çdo hap provon fillimisht harqet me kosto bazë më të ulët. Nëse rruga ngec (nuk ka vazhdim ose kthim te 0), algoritmi kthehet prapa dhe provon harkun tjetër. Implementimi është me stivë (pa rekursion) dhe ka kufi prej 1 000 000 hapash. Kjo rrugë është pika e nisjes për SA dhe ILS.

### 4.2 Lëvizjet dhe kërkimi lokal

- **Insertion i segmentit:** hiqet një segment me 1 … L nyje dhe futet në një pozitë tjetër. Kjo është lëvizje **3-opt që e ruan drejtimin**. Në graf të orientuar kjo ka rëndësi, sepse 2-opt klasik e kthen mbrapsht një segment dhe i ndryshon harqet.
- **Swap:** ndërrohen vendet e dy nyjeve.
- Para vlerësimit kontrollohet që harqet e reja ekzistojnë, dhe lëvizjet e pavlefshme hidhen menjëherë.

**Kërkimi lokal** (first-improvement) provon të gjitha insertion-et dhe swap-et në rend të rastit, e pranon përmirësimin e parë dhe përsërit derisa asnjë lëvizje të mos e përmirësojë rrugën (optimum lokal).

Gjatë zhvillimit vërejtëm se zgjidhjet e versionit të parë të SA-së (segmente 1–3) ishin optimume lokale për lagjen me segmente të shkurtra. Me segmente të çfarëdo gjatësie, disa prej tyre u përmirësuan menjëherë (p.sh. `grf8` nga 55.83 në 53.94). Prandaj algoritmet e reja përdorin segmente më të gjata.

### 4.3 Simulated Annealing (SA)

Në çdo iteracion bëhet një lëvizje e rastit (70% insertion me segment deri në n/2 nyje, 30% swap). Një kandidat më i keq me ndryshim Δ pranohet me probabilitet e^(−Δ/T). Temperatura ulet në mënyrë eksponenciale me kohën, nga 0.5 deri në 0.001 herë kostoja mesatare e një harku. Nëse nuk ka përmirësim pas 20 000 iteracioneve, kërkimi rinis nga zgjidhja më e mirë.

Pranimi implementohet në mënyrë ekuivalente: numri u ~ U(0,1) zgjidhet para vlerësimit, dhe kandidati pranohet nëse Δ ≤ −T·ln(u). Kështu kufiri dihet që më parë dhe vlerësimi mund të ndërpritet herët.

### 4.4 GRASP

GRASP (Greedy Randomized Adaptive Search Procedure) përsërit dy faza sa ka kohë:

1. **Ndërtimi greedy i rastësishëm.** Nga nyja aktuale llogaritet kostoja e çdo harku kandidat **me trigger-at e prefiksit**. Meqë prefiksi është tashmë i fiksuar, kjo kosto është e saktë, ndryshe nga backtracking-u që i sheh vetëm kostot bazë. Ndërtohet lista e kandidatëve të kufizuar (RCL): kandidatët me kosto ≤ c_min + α·(c_max − c_min). Prej saj zgjidhet rastësisht një kandidat. Parametri α zgjidhet rastësisht në [0, 0.3] në çdo iteracion. Nëse ndërtimi ngec, rruga hidhet dhe fillohet një e re.
2. **Kërkimi lokal** me segmente deri në n/4 nyje, që të ketë më shumë iteracione.

Iteracionet janë të pavarura nga njëra-tjetra, dhe ruhet zgjidhja më e mirë.

### 4.5 Iterated Local Search (ILS)

1. Nga rruga e backtracking-ut bëhet kërkim lokal me lagjen e plotë (segmente të çfarëdo gjatësie).
2. Sa ka kohë: zgjidhja më e mirë perturbohet me 3 lëvizje insertion të rastit, bëhet prapë kërkim lokal, dhe rezultati ruhet nëse është më i mirë.

Perturbimi duhet të jetë mjaft i fortë për ta nxjerrë rrugën nga optimumi lokal, por jo aq sa të humbë gjithë strukturën e mirë.

## 5. Analiza e kompleksitetit

Shënimet: n = numri i nyjeve, m = numri i harqeve, r = numri i marrëdhënieve trigger, L = gjatësia maksimale e segmentit, Δ = shkalla maksimale dalëse e një nyjeje.

| Pjesa | Koha | Memoria |
|---|---|---|
| Leximi dhe tabela e trigger-ave | O(m² + r) | O(m²) |
| Vlerësimi i një rruge (rasti më i keq) | O(n²) | O(n) |
| Një iteracion i SA-së | O(n²) | O(n) |
| Ndërtimi i GRASP-it | O(n² · Δ) | O(n) |
| Një kalim i kërkimit lokal | O(n² · L) lëvizje × O(n²) = O(n⁴ · L) | O(n) |
| Backtracking | eksponenciale në rastin më të keq (e kufizuar në 10⁶ hapa) | O(n) |

Vlerësimi është O(n²) sepse për çdo hark kërkohet prapa nëpër prefiks. Në praktikë është shumë më i shpejtë: kërkimi ndalet te trigger-i i parë që gjendet, vlerësimi i pjesshëm i kapërcen harqet e pandryshuara, dhe ndërprerja e hershme i hedh kandidatët e këqij. Tabela O(m²) është e përballueshme për instancat e konkursit (m ≤ 2 700, rreth 58 MB) dhe jep qasje O(1) në marrëdhënie.

Kostoja e lartë e një kalimi të kërkimit lokal shpjegon pse GRASP-i dhe ILS-i bëjnë shumë më pak iteracione se SA-ja (seksioni 6.4), por secili iteracion i tyre është shumë më "i zgjuar".

## 6. Eksperimentet dhe rezultatet

### 6.1 Instancat

| Instanca | Nyje | Harqe | Marrëdhënie trigger | Kopje e |
|---|---:|---:|---:|---|
| `grf1` | 20 | 300 | 5 651 | — |
| `grf2` | 20 | 300 | 5 708 | — |
| `grf3` | 20 | 300 | 55 306 | — |
| `grf4` | 20 | 300 | 58 208 | — |
| `grf5` | 20 | 200 | 1 880 | — |
| `grf6` | 20 | 200 | 1 732 | — |
| `grf7` | 40 | 1 200 | 47 777 | — |
| `grf8` | 40 | 1 200 | 47 281 | — |
| `grf9` | 40 | 1 200 | 909 054 | — |
| `grf10` | 40 | 1 200 | 881 876 | — |
| `grf11` | 40 | 800 | 15 490 | — |
| `grf12` | 40 | 800 | 15 650 | — |
| `grf13` | 60 | 2 700 | 162 514 | — |
| `grf14` | 60 | 2 700 | 160 095 | — |
| `grf15` | 60 | 2 700 | 4 527 944 | — |
| `grf16` | 60 | 2 700 | 4 478 927 | — |
| `grf17` | 60 | 1 800 | 53 313 | — |
| `grf18` | 60 | 1 800 | 53 472 | — |
| `grf19` | 20 | 300 | 5 708 | `grf2` |
| `grf20` | 40 | 1 200 | 47 281 | `grf8` |
| `grf21` | 60 | 2 700 | 160 095 | `grf14` |

`grf19`, `grf20` dhe `grf21` janë kopje identike (bajt për bajt) të `grf2`, `grf8` dhe `grf14`. U ekzekutuan për plotësi, por në statistikat përmbledhëse (fitore, gap) numërohen vetëm **18 instancat unike** `grf1`–`grf18`.

### 6.2 Kushtet e eksperimentit

- **Kompjuteri:** Kaggle Notebook, CPU me 4 bërthama. Të gjitha provat u bënë në të njëjtin ekzekutim, që krahasimi të jetë i drejtë.
- **Koha:** **60 sekonda** për çdo provë, e njëjtë për të tria algoritmet. Kufiri është kohor, jo me numër iteracionesh.
- **Seed-et:** 1, 2, 3, 4, 5 për çdo algoritëm dhe instancë.
- **Gjithsej:** 21 instanca × 3 algoritme × 5 seed-e = **315 prova**, 4 paralelisht.
- **Ekzekutimi:** `python src/main.py te_gjitha --koha 60 --procese 4`, nga notebook-u në Kaggle.

### 6.3 Rezultatet kryesore

Kostoja më e mirë dhe mesatarja nga 5 seed-et. Me të trasha është vlera më e mirë e rreshtit, veç për kolonat “më e mira” dhe veç për “mesatarja”.

| Instanca | SA më e mira | SA mesatarja | GRASP më e mira | GRASP mesatarja | ILS më e mira | ILS mesatarja |
|---|---:|---:|---:|---:|---:|---:|
| `grf1` | **101.13** | **101.13** | **101.13** | **101.13** | **101.13** | **101.13** |
| `grf2` | **44.53** | 44.68 | **44.53** | **44.53** | **44.53** | **44.53** |
| `grf3` | **98.35** | 98.94 | **98.35** | **98.35** | **98.35** | **98.35** |
| `grf4` | **38.59** | **38.59** | **38.59** | **38.59** | **38.59** | **38.59** |
| `grf5` | **113.17** | **113.17** | **113.17** | **113.17** | **113.17** | **113.17** |
| `grf6` | **49.93** | **49.93** | **49.93** | **49.93** | **49.93** | **49.93** |
| `grf7` | 198.98 | 201.01 | 196.34 | 198.40 | **194.06** | **197.25** |
| `grf8` | 54.62 | 55.86 | **52.88** | 54.29 | **52.88** | **52.96** |
| `grf9` | 187.89 | 190.63 | 187.23 | 188.63 | **185.54** | **187.49** |
| `grf10` | **56.30** | 57.93 | **56.30** | 56.49 | **56.30** | **56.30** |
| `grf11` | 208.81 | 210.89 | 207.04 | 209.81 | **206.39** | **207.81** |
| `grf12` | 63.08 | 64.65 | 63.04 | 63.56 | **62.36** | **62.87** |
| `grf13` | 296.12 | 298.69 | 294.52 | 297.80 | **291.48** | **294.95** |
| `grf14` | 63.58 | 65.33 | 64.25 | 66.43 | **63.42** | **64.77** |
| `grf15` | 277.17 | 281.80 | **277.03** | **278.69** | 279.62 | 280.68 |
| `grf16` | 71.38 | 72.61 | **70.02** | 71.39 | 70.05 | **71.12** |
| `grf17` | 303.97 | 305.43 | 303.14 | 303.94 | **301.82** | **303.90** |
| `grf18` | 82.71 | 86.12 | 82.82 | 84.57 | **81.67** | **82.61** |
| `grf19` | **44.53** | **44.53** | **44.53** | **44.53** | **44.53** | **44.53** |
| `grf20` | 54.47 | 55.73 | **52.88** | 54.29 | **52.88** | **52.96** |
| `grf21` | 63.85 | 66.31 | 64.25 | 66.43 | **63.42** | **64.80** |

**Përmbledhje për 18 instancat unike:**

| | SA | GRASP | ILS |
|---|---:|---:|---:|
| Fitore sipas mesatares | 0 | 1 | **11** |
| Fitore sipas më të mirës | 0 | 2 | **8** |
| Gap-i mesatar ndaj më të mirës së njohur | 2.18% | 1.35% | **0.69%** |
| Gap-i mediane | 1.60% | 0.84% | **0.00%** |
| Gap-i maksimal | 9.67% | 9.60% | **6.83%** |
| Provat që arritën më të mirën e njohur | 31.1% | 41.1% | **52.2%** |

Në instancat e tjera ka barazim: 6 sipas mesatares (`grf1`–`grf6`) dhe 8 sipas më të mirës. Gap-i është sa përqind është kostoja e një prove mbi koston më të mirë që gjeti cilido algoritëm për atë instancë.

### 6.4 Qëndrueshmëria dhe numri i iteracioneve

Devijimi standard i kostos nga 5 seed-et (për `grf1`–`grf6` është pothuajse 0 te të tria):

| Instanca | SA | GRASP | ILS |
|---|---:|---:|---:|
| `grf7` | 2.07 | 1.31 | 1.96 |
| `grf8` | 0.82 | 0.72 | 0.15 |
| `grf9` | 2.02 | 1.19 | 1.44 |
| `grf10` | 1.14 | 0.38 | 0.00 |
| `grf11` | 1.63 | 1.64 | 1.02 |
| `grf12` | 1.16 | 0.36 | 0.38 |
| `grf13` | 2.40 | 2.07 | 2.92 |
| `grf14` | 1.92 | 2.05 | 1.54 |
| `grf15` | 3.78 | 1.58 | 1.10 |
| `grf16` | 0.78 | 1.22 | 0.86 |
| `grf17` | 1.09 | 0.45 | 1.73 |
| `grf18` | 2.46 | 1.22 | 0.87 |

Numri mesatar i iteracioneve në 60 s:

| Instanca | n | SA | GRASP | ILS |
|---|---:|---:|---:|---:|
| `grf1` | 20 | 2 752 380 | 890 | 780 |
| `grf5` | 20 | 5 753 220 | 2 682 | 2 489 |
| `grf7` | 40 | 1 087 040 | 31 | 28 |
| `grf9` | 40 | 2 482 080 | 91 | 78 |
| `grf11` | 40 | 3 086 380 | 98 | 90 |
| `grf13` | 60 | 572 800 | 5 | 4 |
| `grf15` | 60 | 1 875 660 | 18 | 15 |
| `grf17` | 60 | 1 756 720 | 12 | 12 |

SA bën miliona iteracione të lira. GRASP-i dhe ILS-i bëjnë vetëm dhjetëra deri në mijëra iteracione, sepse secili përmban një kërkim lokal të plotë. Në instancat me n = 60 (`grf13`, `grf14`) janë vetëm 4–5 iteracione në minutë, dhe megjithatë ILS-i jep rezultatin më të mirë. Kjo tregon se cilësia e lagjes (segmentet e gjata) ka më shumë rëndësi se numri i iteracioneve.

### 6.5 Krahasimi me versionin e parë

Versioni i parë kishte vetëm SA, me segmente 1–3 dhe vlerësim të plotë, 500 000 iteracione ose 60 s, dhe u ekzekutua në kompjuter tjetër. Rezultatet e tij ruhen te `results/sa_v1/`.

| Instanca | Kostoja fillestare (backtracking) | SA v1 | Më e mira e re | Algoritmi | Përmirësimi ndaj SA v1 |
|---|---:|---:|---:|---|---:|
| `grf1` | 123.44 | 101.13 | 101.13 | SA/GRASP/ILS | +0.00% |
| `grf2` | 65.80 | 44.53 | 44.53 | SA/GRASP/ILS | +0.00% |
| `grf3` | 112.38 | 98.35 | 98.35 | SA/GRASP/ILS | +0.00% |
| `grf4` | 60.17 | 38.59 | 38.59 | SA/GRASP/ILS | +0.00% |
| `grf5` | 128.10 | 113.17 | 113.17 | SA/GRASP/ILS | +0.00% |
| `grf6` | 81.75 | 49.93 | 49.93 | SA/GRASP/ILS | +0.00% |
| `grf7` | 231.02 | 193.95 | 194.06 | ILS | -0.06% |
| `grf8` | 73.62 | 55.83 | 52.88 | GRASP/ILS | +5.28% |
| `grf9` | 227.90 | 189.24 | 185.54 | ILS | +1.96% |
| `grf10` | 78.14 | 56.75 | 56.30 | SA/GRASP/ILS | +0.79% |
| `grf11` | 223.67 | 212.64 | 206.39 | ILS | +2.94% |
| `grf12` | 73.80 | 63.92 | 62.36 | ILS | +2.44% |
| `grf13` | 325.41 | 295.75 | 291.48 | ILS | +1.44% |
| `grf14` | 91.95 | 63.81 | 63.42 | ILS | +0.61% |
| `grf15` | 322.37 | 283.88 | 277.03 | GRASP | +2.41% |
| `grf16` | 97.51 | 70.03 | 70.02 | GRASP | +0.01% |
| `grf17` | 340.04 | 303.24 | 301.82 | ILS | +0.47% |
| `grf18` | 128.69 | 87.12 | 81.67 | ILS | +6.26% |

Përmirësimi është në 11 nga 18 instancat. Në 6 instancat e vogla (n = 20) të gjitha versionet gjejnë të njëjtën kosto. Vetëm te `grf7` versioni i parë mbetet pak më i mirë (193.95 kundrejt 194.06).

## 7. Diskutim

- **ILS** del më i miri dhe më i qëndrueshmi. Kombinimi i lagjes së plotë (segmente të çfarëdo gjatësie) me perturbim të vogël e lejon të dalë nga optimumet lokale pa e humbur strukturën e mirë të zgjidhjes.
- **GRASP-i** është i dyti. Pati koston më të mirë në `grf15` dhe `grf16`, instancat me më shumë marrëdhënie trigger (rreth 4.5 milionë), dhe mesataren më të mirë në `grf15`. Aty ndërtimi që i llogarit trigger-at që në fillim jep pika nisjeje shumë më të mira se backtracking-u, që i sheh vetëm kostot bazë. Dobësia e tij është që iteracionet nuk mësojnë nga njëra-tjetra.
- **SA** bën shumë më shumë iteracione, por me lëvizje të rastit. Ka mesataren më të keqe dhe luhatet më shumë nga seed-i në seed. Megjithatë është i thjeshtë dhe nuk ka nevojë për kërkim lokal të shtrenjtë.
- Në instancat e vogla (n = 20) të tria arrijnë të njëjtën kosto. Kjo sugjeron që ajo kosto është afër optimumit, por nuk është provuar optimale.
- Rezultatet për `grf19`–`grf21` dalin pothuajse të njëjta me ato të kopjeve të tyre, gjë që konfirmon që algoritmet janë të qëndrueshme. Dallimet e vogla vijnë nga koha: me kufi kohor, numri i iteracioneve ndryshon pak nga një ekzekutim në tjetrin.

### Kufizimet

- Algoritmet janë heuristika dhe nuk garantojnë optimumin global.
- Zgjidhjet nuk janë kontrolluar ende me validuesin zyrtar të konkursit. U kontrolluan me vlerësuesin e programit dhe me një vlerësues të dytë të pavarur.
- Kufiri kohor e bën rezultatin të varur nga shpejtësia e kompjuterit, prandaj të gjitha provat përfundimtare u bënë në të njëjtin kompjuter.
- `grf15` dhe `grf16` janë shumë të mëdha për GitHub. Për riprodhim duhet të shtohen veçmas (në Kaggle si Dataset).
- Python-i i pastër e kufizon shpejtësinë. Një version me numba ose në gjuhë të kompiluar do të bënte shumë më shumë iteracione.

## 8. Përfundim

U implementuan dhe u krahasuan tre metaheuristika për Trigger Arc TSP mbi të njëjtën bazë kodi: leximi me tabelë kompakte të trigger-ave, vlerësimi i pjesshëm me ndërprerje të hershme, dhe lëvizjet 3-opt që e ruajnë drejtimin. Me kohë të barabartë, **ILS dha rezultatet më të mira dhe më të qëndrueshme**, GRASP-i ishte i dyti dhe më i miri në instancat më të mëdha, ndërsa SA-ja ishte e treta. Krahasuar me versionin e parë, kostot më të mira u përmirësuan deri në 6.26%.

Hapa të mundshëm më tej: kontrolli me validuesin zyrtar, *path relinking* te GRASP-i, kombinimi i ndërtimit të GRASP-it me ILS-in, dhe një version më i shpejtë i funksionit të kostos (numba).

## Si riprodhohen rezultatet

```bash
python src/main.py te_gjitha --koha 60 --procese 4
```

Ose në Kaggle me notebook-un `notebooks/Trigger_Arc_TSP_Kaggle.ipynb`, i cili e ekzekuton programin dhe i nxjerr tabelat dhe grafikët. Rezultatet ruhen veç për secilin algoritëm te `results/sa/`, `results/grasp/` dhe `results/ils/`, ndërsa krahasimi te `results/krahasimi.csv`.

## Referenca

1. C. Cerrone, M. Truvolo, R. Dragone, *The Trigger Arc TSP: Optimise the Picking Process in Warehouses with Compactable Storage Systems*, Springer. https://link.springer.com/chapter/10.1007/978-3-031-78238-1_26
2. J. Salvà Soler, G. de Lambertye, *A Fast GRASP Metaheuristic for the Trigger Arc TSP with MIP-Based Construction and Multi-Neighborhood Local Search*, arXiv:2508.08477, 2025. https://arxiv.org/abs/2508.08477
3. MESS 2024 – Metaheuristics Summer School, konkursi Trigger Arc TSP, Catania, 2024.
4. Kirkpatrick, S., Gelatt, C. D., Vecchi, M. P., *Optimization by Simulated Annealing*, Science, 1983.
5. Feo, T. A., Resende, M. G. C., *Greedy Randomized Adaptive Search Procedures*, Journal of Global Optimization, 1995.
6. Lourenço, H. R., Martin, O. C., Stützle, T., *Iterated Local Search*, Handbook of Metaheuristics, 2003.