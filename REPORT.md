# Zgjidhja heuristike për Trigger Arc TSP

**Lënda:** Dizajni dhe Analiza e Algoritmeve  
**Studentja:** [Emri yt]  
**Data:** [Data e dorëzimit]

## Përmbledhje

Ky projekt trajton Trigger Arc Travelling Salesman Problem (TA-TSP), një variant të problemit të shitësit udhëtues ku kalimi nëpër një hark mund ta ndryshojë koston e një harku tjetër. U implementua një program në Python që lexon instancat, ndërton një cikël fillestar dhe kërkon zgjidhje me Simulated Annealing.

Eksperimentet u kryen në nëntë instanca, `grf1`–`grf9`. Për secilën instancë u përdorën pesë seed-e dhe 10 000 iteracione për seed. Simulated Annealing gjeti kosto më të ulët se ndërtimi fillestar në tetë nga nëntë instancat. Në `grf8`, kostoja më e mirë ishte e barabartë me koston fillestare.

Kodi u optimizua duke përgatitur indekset e harqeve dhe të marrëdhënieve trigger vetëm një herë, pastaj duke i ripërdorur gjatë kërkimit. Në krahasimet e `grf7` dhe `grf8`, kostot për secilin seed mbetën të njëjta, ndërsa koha e ekzekutimit u zvogëlua ndjeshëm.

## 1. Përshkrimi i problemit

Jepet një graf i drejtuar. Kërkohet një cikël Hamiltonian që nis te nyja 0, viziton çdo nyje saktësisht një herë dhe kthehet në nyjën 0.

Një marrëdhënie trigger përmban një hark shkaktar, një hark objektiv dhe një kosto të re. Kur kalohet harku shkaktar, kostoja e harkut objektiv ndryshon nëse harku objektiv nuk është kaluar ende. Për këtë arsye, kostoja përfundimtare varet nga rendi në të cilin kalohen harqet.

## 2. Përfaqësimi dhe llogaritja e kostos

Programi lexon nga skedari numrin e nyjeve, harqeve dhe marrëdhënieve trigger. Çdo hark ruhet me identifikuesin, nyjën fillestare, nyjën përfundimtare dhe koston. Kostot mund të jenë numra dhjetorë.

Funksioni i vlerësimit kontrollon që rruga të jetë cikël Hamiltonian dhe që çdo hark i përdorur të ekzistojë. Gjatë kalimit nëpër rrugë, ai zbaton ndryshimet e kostove nga trigger-at sipas rendit të kalimit.

Për ta shpejtuar vlerësimin, indekset nga nyjet te harqet dhe nga harqet te marrëdhëniet trigger përgatiten një herë dhe ripërdoren gjatë kërkimit. Kostot e ndryshuara nga trigger-at ruhen veçmas nga kostot fillestare.

## 3. Algoritmet

### Ndërtimi fillestar me kthim pas

Ndërtimi fillon në nyjën 0 dhe provon fillimisht harqet me kosto më të ulët. Nëse një zgjedhje e çon rrugën në qorrsokak, algoritmi kthehet pas dhe provon një hark tjetër. Kërkimi ndalet kur gjendet një cikël fillestar i vlefshëm. Në implementim është vendosur kufi prej 1 000 000 thirrjesh kërkimi.

### Simulated Annealing

Simulated Annealing nis nga cikli fillestar dhe krijon rrugë kandidate duke ndërruar ose përmbysur rendin e disa nyjeve. Kandidatët që përdorin harqe që mungojnë refuzohen. Përmirësimet pranohen; disa zgjidhje më të kushtueshme mund të pranohen gjatë kërkimit për të zvogëluar mundësinë e ngecjes në një optimum lokal. Algoritmi ruan rrugën më të mirë që gjen.

## 4. Analiza e kompleksitetit

Përgatitja fillestare e indekseve kushton `O(m + r)`, ku `m` është numri i harqeve dhe `r` numri i marrëdhënieve trigger.

Pas përgatitjes së indekseve, vlerësimi i një rruge kushton `O(n + t)`, ku `n` është numri i nyjeve dhe `t` është numri i marrëdhënieve trigger që lidhen me harqet e kaluara në atë rrugë. Në rastin më të keq, `t` mund të arrijë `r`, prandaj kufiri i sipërm është `O(n + r)`.

Për `K` iteracione, koha e Simulated Annealing është deri në `O(K(n + r))`, pas përgatitjes fillestare të indekseve. Kërkimi fillestar me kthim pas mund të shqyrtojë shumë rrugë në rastin më të keq; implementimi e kufizon në 1 000 000 thirrje kërkimi.

## 5. Eksperimentet dhe rezultatet

Eksperimentet u ekzekutuan me Python 3.12. Për secilën instancë u përdorën pesë seed-e dhe 10 000 iteracione për seed. Mesatarja e kostos dhe kohës u llogarit nga këto pesë prova.

| Instanca | Nyje | Harqe | Marrëdhënie trigger | Kosto fillestare | Kosto mesatare SA | Kostoja më e mirë (seed) | Përmirësimi më i mirë | Koha mesatare për seed | Versioni i matur |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `grf1` | 20 | 300 | 5 651 | 123.44 | 113.49 | 111.34 (5) | 9.8% | 11.22 s | Para optimizimit |
| `grf2` | 20 | 300 | 5 708 | 65.80 | 53.13 | 49.88 (2) | 24.2% | 10.88 s | Para optimizimit |
| `grf3` | 20 | 300 | 55 306 | 112.38 | 111.13 | 108.24 (1) | 3.7% | 98.37 s | Para optimizimit |
| `grf4` | 20 | 300 | 58 208 | 60.17 | 47.21 | 44.50 (1) | 26.0% | 104.45 s | Para optimizimit |
| `grf5` | 20 | 300 | — | 128.10 | 126.19 | 125.27 (2) | 2.2% | 4.20 s | Para optimizimit |
| `grf6` | 20 | 200 | 1 732 | 81.75 | 72.08 | 68.29 (5) | 16.5% | 3.84 s | Para optimizimit |
| `grf7` | 40 | 1 200 | 47 777 | 231.02 | 230.18 | 227.25 (2) | 1.6% | 1.95 s | Pas optimizimit |
| `grf8` | 40 | 1 200 | 47 281 | 73.62 | 73.62 | 73.62 (1–5) | 0.0% | 1.65 s | Pas optimizimit |
| `grf9` | 40 | 1 200 | 909 054 | 227.90 | 221.36 | 218.47 (5) | 4.1% | 28.71 s | Pas optimizimit |

### Krahasimi i optimizimit

Për `grf7` dhe `grf8`, versionet e vjetra dhe të optimizuara u ekzekutuan me të njëjtët seed-e dhe të njëjtin numër iteracionesh. Në të dy rastet, kostot për seed mbetën të njëjta.

| Instanca | Koha mesatare para optimizimit | Koha mesatare pas optimizimit | Përshpejtimi i përafërt | Kostot për seed |
|---|---:|---:|---:|---|
| `grf7` | 95.40 s | 1.95 s | 48.9 herë | Të njëjta |
| `grf8` | 94.93 s | 1.65 s | 57.5 herë | Të njëjta |

Për `grf8`, në CSV ruhen disa ekzekutime. Në tabelën kryesore është përdorur grupi më i fundit i versionit të optimizuar për kohën mesatare. Grupet e tjera shërbejnë për krahasimin e kohës dhe nuk duhen numëruar si seed-e të reja.

## 6. Diskutim dhe kufizime

Simulated Annealing gjeti të paktën një kosto më të ulët se ndërtimi fillestar në tetë instanca. Përmirësimet më të mëdha u arritën në `grf2` dhe `grf4`. Në `grf8`, të pesë seed-et përfunduan me të njëjtën rrugë dhe kosto si zgjidhja fillestare; në provat e kryera algoritmi nuk e përmirësoi atë.

Krahasimet e `grf7` dhe `grf8` treguan se optimizimi e zvogëloi kohën e ekzekutimit pa ndryshuar kostot për seed. Kohët e `grf1`–`grf6` janë matur me versionin e mëparshëm të kodit; ato nuk janë rimatur ende me versionin e optimizuar.

CSV-ja përmban ekzekutime të përsëritura. Për llogaritjet statistikore, secili seed duhet të numërohet vetëm një herë për secilën instancë dhe version të kodit. Ekzekutimet e vjetra dhe të reja të `grf7` e `grf8` përdoren për krahasimin e performancës.

Rrugët nuk janë kontrolluar ende me validuesin zyrtar të konkursit; vlefshmëria zyrtare mbetet e pakontrolluar. Simulated Annealing është heuristikë dhe nuk garanton optimumin global. Janë provuar vetëm instancat `grf1`–`grf9`, jo të gjitha instancat e publikuara.

## 7. Përfundim

U implementua një zgjidhës për TA-TSP që lexon instancat, ndërton një cikël fillestar me kthim pas dhe kërkon përmirësim me Simulated Annealing. Në tetë nga nëntë instancat e provuara, algoritmi gjeti të paktën një kosto më të ulët se ajo e ciklit fillestar.

Optimizimi ruajti të njëjtat kosto në krahasimet e `grf7` dhe `grf8`, ndërsa e shpejtoi ekzekutimin rreth 48.9 dhe 57.5 herë, përkatësisht. Për një vlerësim më të plotë, instancat e mbetura duhet të provohen me versionin e optimizuar dhe zgjidhjet duhet të kontrollohen me validuesin zyrtar.

## Referenca

Cerrone, C., Cerulli, R., Ceschia, S. dhe Schaerf, A. *Metaheuristics Summer School Competition: The Trigger Arc TSP*, MESS 2024, prezantimi i dhënë për projektin.