# Zgjidhja heuristike për Trigger Arc TSP

**Lënda:** Dizajni dhe Analiza e Algoritmeve  
**Studentja:** Pranvera Gashi  
**Data:** [Data e dorëzimit]  
**Kodi:** https://github.com/Pranvera08/Pranvera-Gashi-The-Trigger-Arc-TSP  
**Notebook-u në Kaggle:** [linku i notebook-ut publik]

## Përmbledhje

Ky projekt trajton Trigger Arc Travelling Salesman Problem (TA-TSP). Është një variant i problemit të shitësit udhëtues, ku kalimi nëpër një hark mund ta ndryshojë koston e një harku tjetër që kalohet më vonë. Problemi është paraqitur në konkursin MESS 2024 (Catania).

U implementuan në Python tre algoritme metaheuristike: **Simulated Annealing (SA)**, **GRASP** dhe **Iterated Local Search (ILS)**. Ato ndajnë të njëjtin funksion të kostos, të njëjtat lëvizje dhe të njëjtin kërkim lokal. Algoritmet u testuan në të dy grupet e instancave të konkursit: **21 instanca të grupit të parë** (grafe të dendura, 20–60 nyje) dhe **34 instanca të grupit të dytë** (grafe të rralla, 18–142 nyje), gjithsej 55 instanca. Çdo algoritëm u ekzekutua me 5 seed-e dhe 60 sekonda për provë, në Kaggle (4 bërthama CPU), gjithsej 825 prova.

Rezultati kryesor: **ILS ishte algoritmi më i mirë në përgjithësi**. Ai pati mesataren më të ulët në 34 nga 52 instancat unike (11 nga 18 në grupin e parë dhe 23 nga 34 në të dytin) dhe arriti zgjidhjen më të mirë në 34% të provave. **GRASP-i ishte më i qëndrueshmi**, sidomos në grafet e rralla, ku gap-i i tij nuk e kaloi kurrë 0.64%. SA-ja ishte e treta. Për grafet e rralla të grupit të dytë u zhvillua një ndërtim i ri i zgjidhjes fillestare (rregulli i Warnsdorff-it me prerje), pa të cilin metoda e parë nuk gjente cikël në 31 nga 34 instancat. Krahasuar me versionin e parë të projektit (vetëm SA), kostoja më e mirë u përmirësua në 11 nga 18 instancat e grupit të parë, deri në 6.26%. Me post-optimizim (ILS i nisur nga zgjidhja më e mirë e njohur), rekordet u përmirësuan edhe në 25 instanca, deri në 2.27%.

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

Çdo zgjidhje përfundimtare kontrollohet me një vlerësim të plotë: cikël Hamiltonian, harqe që ekzistojnë, kosto e rillogaritur. Pas eksperimenteve, zgjidhjet u verifikuan edhe me një vlerësues të pavarur me qasje tjetër (fjalor i trigger-ave aktivë gjatë kalimit). Të 159 zgjidhjet e algoritmeve dhe 53 rekordet e post-optimizimit që mund të kontrollohen përputhen saktësisht. `grf15`/`grf16` nuk janë në repo, prandaj atyre iu kontrollua vetëm vlefshmëria e ciklit.

## 4. Algoritmet

### 4.1 Ndërtimi fillestar me kthim pas (backtracking)

Ndërtimi nis te nyja 0 dhe në çdo hap provon fillimisht harqet me kosto bazë më të ulët. Nëse rruga ngec (nuk ka vazhdim ose kthim te 0), algoritmi kthehet prapa dhe provon harkun tjetër. Implementimi është me stivë (pa rekursion) dhe ka kufi prej 1 000 000 hapash. Kjo rrugë është pika e nisjes për SA dhe ILS.

**Grafet e rralla (grupi i dytë).** Në grafet ku çdo nyje ka vetëm 5–11 harqe dalëse, ky kërkim nuk gjeti cikël në 31 nga 34 instancat. Prandaj, kur metoda e parë dështon, përdoret një kërkim i dytë me dy përmirësime:

1. **Rregulli i Warnsdorff-it:** fillimisht provohet fqinji me më pak vazhdime të lira, me koston bazë si kriter të dytë. Nyjet "e vështira" vizitohen sa kanë ende rrugë.
2. **Prerja:** një degë braktiset menjëherë nëse ndonjë nyje e pavizituar nuk ka më asnjë hyrje ose dalje të mundshme, ose nëse nuk ka mbetur asnjë nyje e pavizituar me hark kthimi te 0.

Me këtë kërkim u gjet cikël në të 55 instancat, për më pak se 0.5 s. Për grupin e parë rruga fillestare mbetet e njëjtë, sepse kërkimi i dytë përdoret vetëm kur i pari dështon.

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

**Në grafe të rralla** ndërtimi greedy i rastësishëm ngec pothuajse gjithmonë: te instancat me 58+ nyje të grupit të dytë nuk u ndërtua asnjë rrugë e vlefshme. Prandaj, nëse ndërtimi dështon 200 herë rresht pa asnjë sukses, GRASP-i kalon në një ndërtim me kthim pas të kufizuar dhe me prerjen e mësipërme. RCL-ja sipas kostos ndërtohet brenda fqinjëve me shkallë minimale të Warnsdorff-it (ose +1), kështu që zgjedhja mbetet greedy e rastësishme, por shmang rrugët pa dalje. Me këtë ndërtim, mbi 90% e ndërtimeve kanë sukses edhe te `grf134` (142 nyje).

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
| Kontrolli i prerjes (Warnsdorff) për një hap | O(n · Δ) | O(n) |
| Ndërtimi me Warnsdorff dhe prerje | O(K · n · Δ) për K hapa kërkimi | O(n) |

Vlerësimi është O(n²) sepse për çdo hark kërkohet prapa nëpër prefiks. Në praktikë është shumë më i shpejtë: kërkimi ndalet te trigger-i i parë që gjendet, vlerësimi i pjesshëm i kapërcen harqet e pandryshuara, dhe ndërprerja e hershme i hedh kandidatët e këqij. Tabela O(m²) është e përballueshme për instancat e konkursit (m ≤ 2 700 në grupin e parë dhe m ≤ 1 562 në të dytin, rreth 58 MB në rastin më të madh) dhe jep qasje O(1) në marrëdhënie.

Kostoja e lartë e një kalimi të kërkimit lokal shpjegon pse GRASP-i dhe ILS-i bëjnë shumë më pak iteracione se SA-ja (seksioni 6.4), por secili iteracion i tyre është shumë më "i zgjuar".

## 6. Eksperimentet dhe rezultatet

### 6.1 Instancat

Instancat janë marrë nga faqja e konkursit MESS 2024 (faqja *Info*), ku publikohen në dy grupe.

**Grupi i parë (21 instanca, grafe të dendura):**

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

**Grupi i dytë (34 instanca, grafe të rralla):** `grf101`–`grf134`, me 18–142 nyje, 90–1 562 harqe dhe deri në 208 020 marrëdhënie trigger. Çdo nyje ka vetëm 5–11 harqe dalëse, ndërsa në grupin e parë ka 10–45. Asnjë instancë e grupit të dytë nuk është kopje. Madhësitë e secilës janë në tabelën e seksionit 6.4.

### 6.2 Kushtet e eksperimentit

- **Kompjuteri:** Kaggle Notebook, CPU me 4 bërthama, i njëjti lloj për të dy grupet. Grupi i parë u ekzekutua në një version të notebook-ut dhe grupi i dytë në një tjetër, me të njëjtat parametra.
- **Koha:** **60 sekonda** për çdo provë, e njëjtë për të tria algoritmet. Kufiri është kohor, jo me numër iteracionesh.
- **Seed-et:** 1, 2, 3, 4, 5 për çdo algoritëm dhe instancë.
- **Gjithsej:** (21 + 34) instanca × 3 algoritme × 5 seed-e = **825 prova**, 4 paralelisht.
- **Ekzekutimi:** `python src/main.py <instancat> --koha 60 --procese 4`, nga notebook-u në Kaggle.

### 6.3 Rezultatet: grupi i parë

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

### 6.4 Rezultatet: grupi i dytë

Kostoja më e mirë dhe mesatarja nga 5 seed-et, me 60 s për provë. Me të trasha është vlera më e mirë e rreshtit, veç për "më e mira" dhe veç për "mesatarja".

| Instanca | n | Harqe | Marrëdhënie | SA më e mira | SA mesatarja | GRASP më e mira | GRASP mesatarja | ILS më e mira | ILS mesatarja |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `grf101` | 18 | 90 | 1 144 | **16.96** | **16.96** | 16.97 | 16.97 | **16.96** | 17.04 |
| `grf102` | 22 | 132 | 2 135 | **20.49** | 20.56 | **20.49** | **20.49** | 20.62 | 20.62 |
| `grf103` | 22 | 110 | 1 824 | 20.67 | 20.67 | **20.54** | **20.54** | 20.67 | 20.77 |
| `grf104` | 27 | 162 | 3 410 | 25.14 | 25.18 | 25.14 | 25.15 | **25.12** | **25.13** |
| `grf105` | 26 | 130 | 2 664 | **24.26** | 24.29 | **24.26** | **24.26** | **24.26** | **24.26** |
| `grf106` | 32 | 192 | 4 985 | **29.57** | **29.63** | **29.57** | 29.65 | **29.57** | 29.64 |
| `grf107` | 37 | 222 | 6 860 | **34.22** | 34.27 | **34.22** | **34.23** | 34.25 | 34.27 |
| `grf108` | 37 | 222 | 6 860 | 34.25 | 34.27 | 34.21 | 34.30 | **34.20** | **34.25** |
| `grf109` | 37 | 222 | 6 860 | 34.34 | 34.39 | 34.28 | **34.29** | **34.24** | 34.32 |
| `grf110` | 37 | 222 | 6 860 | **34.31** | 34.35 | 34.32 | **34.32** | 34.36 | 34.36 |
| `grf111` | 42 | 252 | 9 035 | 41.85 | 42.10 | **38.78** | **38.85** | 41.16 | 41.45 |
| `grf112` | 50 | 350 | 15 168 | 46.18 | 46.24 | 46.13 | 46.17 | **46.07** | **46.14** |
| `grf113` | 58 | 464 | 23 583 | 55.58 | 56.27 | **53.46** | **53.49** | 55.35 | 55.60 |
| `grf114` | 66 | 594 | 34 640 | 60.78 | 60.84 | 60.74 | 60.80 | **60.59** | **60.67** |
| `grf115` | 74 | 740 | 48 699 | 67.84 | 68.01 | 67.94 | 68.01 | **67.79** | **67.90** |
| `grf116` | 82 | 902 | 66 120 | 75.23 | 75.32 | 75.22 | 75.30 | **75.08** | **75.18** |
| `grf117` | 52 | 312 | 14 285 | **47.98** | 48.08 | 48.08 | 48.13 | 48.00 | **48.00** |
| `grf118` | 62 | 434 | 23 988 | 56.94 | 57.03 | 57.00 | 57.09 | **56.88** | **56.97** |
| `grf119` | 72 | 576 | 37 303 | 66.09 | 66.25 | 66.15 | 66.23 | **66.01** | **66.12** |
| `grf120` | 82 | 738 | 54 800 | 75.46 | 75.56 | 75.42 | 75.46 | **75.26** | **75.32** |
| `grf121` | 92 | 920 | 77 049 | 84.44 | 84.62 | 84.48 | 84.51 | **84.20** | **84.35** |
| `grf122` | 102 | 1 122 | 104 620 | 93.52 | 93.63 | 93.54 | 93.66 | **93.33** | **93.44** |
| `grf123` | 62 | 372 | 20 735 | 57.32 | 57.37 | 57.12 | 57.25 | **57.03** | **57.12** |
| `grf124` | 74 | 518 | 34 824 | 68.03 | 68.29 | 68.16 | 68.19 | **67.95** | **67.99** |
| `grf125` | 86 | 688 | 54 159 | 79.09 | 79.25 | 78.96 | 79.08 | **78.91** | **78.95** |
| `grf126` | 98 | 882 | 79 568 | 89.91 | 90.02 | 89.98 | 90.07 | **89.75** | **89.84** |
| `grf127` | 110 | 1 100 | 111 879 | 100.90 | 101.08 | 100.74 | 100.91 | **100.61** | **100.71** |
| `grf128` | 122 | 1 342 | 151 920 | 111.73 | 111.87 | 111.82 | 111.88 | **111.53** | **111.69** |
| `grf129` | 72 | 432 | 28 385 | 66.59 | 66.68 | 66.43 | 66.51 | **66.25** | **66.38** |
| `grf130` | 86 | 602 | 47 676 | 79.28 | 79.34 | 79.12 | 79.21 | **78.89** | **78.97** |
| `grf131` | 100 | 800 | 74 151 | 91.97 | 92.04 | 91.86 | 91.97 | **91.60** | **91.71** |
| `grf132` | 114 | 1 026 | 108 944 | 104.59 | 104.83 | 104.60 | 104.67 | **104.30** | **104.43** |
| `grf133` | 128 | 1 280 | 153 189 | 125.67 | 127.05 | **117.17** | **117.32** | 123.61 | 124.61 |
| `grf134` | 142 | 1 562 | 208 020 | 130.33 | 130.40 | 130.06 | 130.19 | **129.84** | **129.95** |

**Përmbledhje për 34 instancat e grupit të dytë:**

| | SA | GRASP | ILS |
|---|---:|---:|---:|
| Fitore sipas mesatares | 2 | 8 | **23** |
| Fitore sipas më të mirës | 2 | 4 | **23** |
| Gap-i mesatar ndaj më të mirës së njohur | 0.98% | **0.24%** | 0.68% |
| Gap-i mediane | 0.38% | 0.26% | **0.14%** |
| Gap-i maksimal | 9.62% | **0.64%** | 7.56% |
| Provat që arritën më të mirën e njohur | 8.8% | 13.5% | **23.5%** |
| Devijimi standard mesatar nga seed-et | 0.122 | **0.043** | 0.093 |

Në 1 instancë ka barazim sipas mesatares dhe në 5 sipas më të mirës.

**Përmbledhje për të gjitha 52 instancat unike (18 + 34):**

| | SA | GRASP | ILS |
|---|---:|---:|---:|
| Fitore sipas mesatares | 2 | 9 | **34** |
| Fitore sipas më të mirës | 2 | 6 | **31** |
| Gap-i mesatar | 1.40% | **0.62%** | 0.68% |
| Gap-i mediane | 0.44% | 0.28% | **0.13%** |
| Provat që arritën më të mirën e njohur | 16.5% | 23.1% | **33.5%** |

Barazim ka në 7 instanca sipas mesatares dhe në 13 sipas më të mirës.

### 6.5 Qëndrueshmëria dhe numri i iteracioneve

Devijimi standard i kostos nga 5 seed-et në grupin e parë (për `grf1`–`grf6` është pothuajse 0 te të tria):

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

Numri mesatar i iteracioneve në 60 s, grupi i parë:

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

Numri mesatar i iteracioneve në 60 s, grupi i dytë:

| Instanca | n | SA | GRASP | ILS |
|---|---:|---:|---:|---:|
| `grf101` | 18 | 9 082 380 | 8 774 | 21 554 |
| `grf110` | 37 | 8 747 020 | 1 363 | 2 268 |
| `grf116` | 82 | 5 395 200 | 54 | 77 |
| `grf122` | 102 | 5 544 060 | 33 | 48 |
| `grf128` | 122 | 5 480 080 | 23 | 32 |
| `grf134` | 142 | 5 281 660 | 16 | 24 |

Në grafet e rralla SA "bën" miliona iteracione, por shumica e lëvizjeve hidhen menjëherë, sepse krijojnë harqe që nuk ekzistojnë. Te instancat më të mëdha (`grf134`, 142 nyje) GRASP-i dhe ILS-i bëjnë vetëm 16–24 iteracione në minutë.

### 6.6 Krahasimi me versionin e parë

Versioni i parë kishte vetëm SA dhe vetëm grupin e parë të instancave, me segmente 1–3 dhe vlerësim të plotë, 500 000 iteracione ose 60 s, dhe u ekzekutua në kompjuter tjetër. Rezultatet e tij ruhen te `results/sa_v1/`.

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

## 7. Post-optimizimi: zgjidhjet më të mira të njohura

Pas eksperimenteve u bë edhe një hap i veçantë post-optimizimi (`python src/main.py te_gjitha --permireso --koha 60 --raunde 3`). Për çdo instancë merret zgjidhja më e mirë e njohur (nga SA, GRASP, ILS ose SA v1) dhe ILS-i niset prej saj me 4 seed-e paralelisht, 60 s për raund. Nëse raundi e përmirëson rekordin, raundi tjetër nis nga rekordi i ri, deri në 3 raunde. Për grupin e parë u bënë dy ekzekutime të tilla njëri pas tjetrit, ku i dyti vazhdoi nga rekordet e të parit. Rekordet ruhen te `results/me_te_mirat_e_njohura/`.

**Këto rezultate nuk krahasohen me tabelat e seksionit 6.** Post-optimizimi merr shumë më shumë kohë gjithsej dhe nis nga rezultatet e algoritmeve, prandaj nuk është krahasim i drejtë mes algoritmeve. Rezultatet e `results/sa`, `grasp` dhe `ils` nuk preken.

Instancat ku u gjet rekord i ri:

| Instanca | Më e mira e algoritmeve (60 s) | Burimi | **Rekordi** | Përmirësimi |
|---|---:|---|---:|---:|
| `grf7` | 193.95 | SA v1 | **191.82** | 1.10% |
| `grf9` | 185.54 | ILS | **183.35** | 1.18% |
| `grf11` | 206.39 | ILS | **206.20** | 0.09% |
| `grf13` | 291.48 | ILS | **290.26** | 0.42% |
| `grf14` | 63.42 | ILS | **62.04** | 2.18% |
| `grf15` | 277.03 | GRASP | **276.97** | 0.02% |
| `grf16` | 70.02 | GRASP | **68.43** | 2.27% |
| `grf17` | 301.82 | ILS | **296.24** | 1.85% |
| `grf18` | 81.67 | ILS | **80.58** | 1.33% |
| `grf111` | 38.78 | GRASP | **38.74** | 0.10% |
| `grf112` | 46.07 | ILS | **46.06** | 0.02% |
| `grf113` | 53.46 | GRASP | **53.32** | 0.26% |
| `grf115` | 67.79 | ILS | **67.77** | 0.03% |
| `grf116` | 75.08 | ILS | **75.07** | 0.01% |
| `grf120` | 75.26 | ILS | **75.15** | 0.15% |
| `grf122` | 93.33 | ILS | **93.22** | 0.12% |
| `grf125` | 78.91 | ILS | **78.88** | 0.04% |
| `grf126` | 89.75 | ILS | **89.68** | 0.08% |
| `grf127` | 100.61 | ILS | **100.45** | 0.16% |
| `grf128` | 111.53 | ILS | **111.39** | 0.13% |
| `grf129` | 66.25 | ILS | **66.19** | 0.09% |
| `grf131` | 91.60 | ILS | **91.49** | 0.12% |
| `grf132` | 104.30 | ILS | **104.22** | 0.08% |
| `grf133` | 117.17 | GRASP | **116.81** | 0.31% |
| `grf134` | 129.84 | ILS | **129.61** | 0.18% |

Gjithsej u përmirësuan **25 nga 52** instancat unike: 9 në grupin e parë (deri në 2.27%, te `grf16`) dhe 16 në të dytin (deri në 0.31%, te `grf133`). Përmirësimet në grupin e dytë janë më të vogla, sepse aty algoritmet ishin tashmë shumë afër njëri-tjetrit. Kjo tregon se ILS-i nga një pikënisje e mirë mund ta përmirësojë zgjidhjen më shumë sesa kur nis nga rruga e backtracking-ut: koha nuk harxhohet për të arritur te zona e mirë.

## 8. Diskutim

- **ILS** del më i miri dhe më i qëndrueshmi. Kombinimi i lagjes së plotë (segmente të çfarëdo gjatësie) me perturbim të vogël e lejon të dalë nga optimumet lokale pa e humbur strukturën e mirë të zgjidhjes.
- **GRASP-i** është i dyti. Pati koston më të mirë në `grf15` dhe `grf16`, instancat me më shumë marrëdhënie trigger (rreth 4.5 milionë), dhe mesataren më të mirë në `grf15`. Aty ndërtimi që i llogarit trigger-at që në fillim jep pika nisjeje shumë më të mira se backtracking-u, që i sheh vetëm kostot bazë. Dobësia e tij është që iteracionet nuk mësojnë nga njëra-tjetra.
- **SA** bën shumë më shumë iteracione, por me lëvizje të rastit. Ka mesataren më të keqe dhe luhatet më shumë nga seed-i në seed. Megjithatë është i thjeshtë dhe nuk ka nevojë për kërkim lokal të shtrenjtë.
- Në instancat e vogla (n = 20) të tria arrijnë të njëjtën kosto. Kjo sugjeron që ajo kosto është afër optimumit, por nuk është provuar optimale.
- **Dallimi mes grupeve.** Në grafet e dendura (grupi i parë) ILS-i dominon qartë. Në grafet e rralla (grupi i dytë) ILS-i fiton në shumicën e instancave, sidomos te ato të mëdha (`grf114`–`grf134`), por GRASP-i është më i qëndrueshmi. Arsyeja është pikënisja: SA dhe ILS nisin nga e njëjta rrugë fillestare (Warnsdorff), dhe në graf të rrallë shumica e lëvizjeve krijojnë harqe që nuk ekzistojnë. Te `grf111`, `grf113` dhe `grf133` kjo i la SA-në dhe ILS-in 4–9% më keq se GRASP-i, i cili ndërton qindra rrugë të ndryshme. Pra, në grafe të rralla diversiteti i pikënisjeve ka më shumë rëndësi sesa në grafe të dendura.
- Rezultatet për `grf19`–`grf21` dalin pothuajse të njëjta me ato të kopjeve të tyre, gjë që konfirmon që algoritmet janë të qëndrueshme. Dallimet e vogla vijnë nga koha: me kufi kohor, numri i iteracioneve ndryshon pak nga një ekzekutim në tjetrin.

### Kufizimet

- Algoritmet janë heuristika dhe nuk garantojnë optimumin global.
- Validuesi zyrtar i konkursit (*Test a Solution*) nuk mund të përdorej, sepse pas përfundimit të garës portali nuk ofron më instanca për testim. Zgjidhjet u verifikuan me vlerësuesin e programit dhe me një vlerësues të dytë të pavarur, që i zbatojnë rregullat e konkursit.
- Kufiri kohor e bën rezultatin të varur nga shpejtësia e kompjuterit, prandaj të gjitha provat përfundimtare u bënë në të njëjtin lloj kompjuteri (Kaggle CPU).
- `grf15` dhe `grf16` janë shumë të mëdha për GitHub. Për riprodhim duhet të shtohen veçmas (në Kaggle si Dataset).
- Python-i i pastër e kufizon shpejtësinë. Një version me numba ose në gjuhë të kompiluar do të bënte shumë më shumë iteracione.

## 9. Përfundim

U implementuan dhe u krahasuan tre metaheuristika për Trigger Arc TSP mbi të njëjtën bazë kodi: leximi me tabelë kompakte të trigger-ave, vlerësimi i pjesshëm me ndërprerje të hershme, lëvizjet 3-opt që e ruajnë drejtimin, dhe ndërtimi me rregullin e Warnsdorff-it dhe prerje për grafe të rralla. Në të 55 instancat e konkursit, me kohë të barabartë, **ILS dha rezultatet më të mira** (mesatarja më e mirë në 34 nga 52 instanca unike), **GRASP-i ishte më i qëndrueshmi**, veçanërisht në grafet e rralla, ndërsa SA-ja ishte e treta. Krahasuar me versionin e parë, kostot më të mira u përmirësuan deri në 6.26%, dhe me post-optimizim u gjetën rekorde të reja në 25 instanca.

Hapa të mundshëm më tej: ILS i nisur nga ndërtimet e GRASP-it për grafe të rralla, *path relinking* te GRASP-i, dhe një version më i shpejtë i funksionit të kostos (numba).

## Si riprodhohen rezultatet

```bash
python src/main.py te_gjitha --koha 60 --procese 4                 # të tria algoritmet
python src/main.py te_gjitha --permireso --koha 60 --raunde 3      # post-optimizimi
```

Ose në Kaggle me notebook-un `notebooks/Trigger_Arc_TSP_Kaggle.ipynb`, i cili e ekzekuton programin dhe i nxjerr tabelat dhe grafikët. Rezultatet ruhen veç për secilin algoritëm te `results/sa/`, `results/grasp/` dhe `results/ils/`, ndërsa krahasimi te `results/krahasimi.csv`.

## Referenca

1. C. Cerrone, M. Truvolo, R. Dragone, *The Trigger Arc TSP: Optimise the Picking Process in Warehouses with Compactable Storage Systems*, Springer. https://link.springer.com/chapter/10.1007/978-3-031-78238-1_26
2. J. Salvà Soler, G. de Lambertye, *A Fast GRASP Metaheuristic for the Trigger Arc TSP with MIP-Based Construction and Multi-Neighborhood Local Search*, arXiv:2508.08477, 2025. https://arxiv.org/abs/2508.08477
3. MESS 2024 – Metaheuristics Summer School, konkursi Trigger Arc TSP, Catania, 2024.
4. Kirkpatrick, S., Gelatt, C. D., Vecchi, M. P., *Optimization by Simulated Annealing*, Science, 1983.
5. Feo, T. A., Resende, M. G. C., *Greedy Randomized Adaptive Search Procedures*, Journal of Global Optimization, 1995.
6. Lourenço, H. R., Martin, O. C., Stützle, T., *Iterated Local Search*, Handbook of Metaheuristics, 2003.