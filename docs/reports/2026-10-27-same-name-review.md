# Same-name groups outside courts: review list, 2026-10-27

Read-only analysis of `data/consolidated/institutii.csv` (v0.26.0). No record changed.

## Method
- Group: same county and same folded name (punctuation, diacritics, case, word order and small words ignored).
- Dropped: groups with two ANAF CIFs (ANAF treats them as different bodies), local kinds (schools, kindergartens, libraries, local councils, numbered units), generic names, courts.
- Dropped counts: {'two ANAF CIFs': 89, 'local kind or generic': 70}.
- By source combination: registrul 31, declaratii+registrul 19, declaratii 13, anaf+declaratii 12, anaf+declaratii+registrul 9, declaratii+roepas 2, anaf+declaratii+registrul+roepas 1, declaratii+registrul+roepas 1, anaf+registrul 1.
- Left for review: **89 groups**. Evidence per group: the record ids, source combination, parent CIFs and ANAF address.

## Why these are not merged yet
The existing same-name rule needs the exact folded name and one record per source. These groups fail because the spelling differs ("Politie"/"Poliţie" with a cedilla, "JUD."/"JUDETEAN"), or because a source holds the name twice. A new rule would need your confirmation: **same county + same normalised name + not a local kind = one body**.

## Groups
### Spitalul Judetean de Urgenta Bistrita (Bistrita Nasaud)
- `G06237` Spitalul Judetean de Urgenta Bistrita — registrul
- `G06238` SPITALUL JUDETEAN DE URGENTA BISTRITA — registrul
- `Db643856c` SPITALUL JUDETEAN DE URGENTA BISTRITA — declaratii
### DIRECTIA LOCALA DE EVIDENTA A PERSOANELOR Sector 6 (Bucuresti)
- `G10360` DIRECTIA LOCALA DE EVIDENTA A PERSOANELOR Sector 6 — registrul
- `G10361` Directia Locala de Evidenta a Persoanelor Sector 6 — registrul
- `D1c4869da` DIRECTIA LOCALA DE EVIDENTA PERSOANELOR SECTOR 6 — declaratii
### APIA - CENTRUL JUDETEAN BUZAU (Buzau)
- `G11010` APIA - CENTRUL JUDETEAN BUZAU — registrul
- `Db8b45793` APIA CENTRUL JUDETEAN BUZAU — declaratii
- `D55b3a2b4` APIA BUZAU CENTRUL JUDETEAN — declaratii
### ORGANISMUL INTERMEDIAR REGIONAL PENTRU PROGRAMUL OPERATIONAL SECTORIAL DEZVOLTAREA RESURSELOR UMANE REGIUNEA NORD VEST (Cluj)
- `D37f100f8` ORGANISMUL INTERMEDIAR REGIONAL PENTRU PROGRAMUL OPERATIONAL SECTORIAL DEZVOLTAREA RESURSELOR UMANE REGIUNEA NORD VEST — declaratii
- `D1e309fa1` ORGANISMUL INTERMEDIAR REGIONAL PENTRU PROGRAMUL OPERATIONAL SECTORIAL PENTRU DEZVOLTAREA RESURSELOR UMANE REGIUNEA NORD VEST — declaratii
- `De7273bc5` ORGANISMUL INTERMEDIAR REGIONAL PROGRAMUL OPERATIONAL SECTORIAL DEZVOLTAREA RESURSELOR UMANE REGIUNEA NORD VEST — declaratii
### Agenția pentru Protecția Mediului Harghita (Harghita)
- `G22001` Agenția pentru Protecția Mediului Harghita — registrul
- `G22010` AGENTIA PENTRU PROTECTIA MEDIULUI HARGHITA — registrul
- `D21da55f1` AGENTIA PENTRU PROTECTIA MEDIULUI HARGHITA — declaratii
### INSPECTORATUL DE POLIŢIE JUDEŢEAN VALCEA (Valcea)
- `G40002` INSPECTORATUL DE POLIŢIE JUDEŢEAN VALCEA — registrul
- `G40072` INSPECTORATUL DE POLITIE JUDETEAN VALCEA — registrul
- `D9c68db53` INSPECTORATUL DE POLITIE JUDETEAN VALCEA — declaratii
### INSPECTORATUL JUD.POLITIE ALBA (Alba)
- `A4331058` INSPECTORATUL JUD.POLITIE ALBA — anaf; parents 4267095; Alba, Municipiul Alba Iulia, STRADA I.C.BRATIANU, Numar 1 B, Bloc/Scar
- `D51abcbeb` INSPECTORATUL JUD POLITIE ALBA — declaratii
### SERVICIUL PUBLIC COMUNITAR LOCAL DE EVIDENTA A PERSOANELOR (Alba)
- `Dc2407686` SERVICIUL PUBLIC COMUNITAR LOCAL DE EVIDENTA A PERSOANELOR — declaratii
- `D276e94c1` SERVICIUL PUBLIC LOCAL COMUNITAR DE EVIDENTA A PERSOANELOR — declaratii
### Directia Judeteana pentru Tineret Arad (Arad)
- `G02161` Directia Judeteana pentru Tineret Arad — registrul
- `G02162` DIRECTIA JUDETEANA PENTRU TINERET ARAD — registrul
### R.A. "Administratia Zonei Libere Curtici - Arad" (Arad)
- `G02187` R.A. "Administratia Zonei Libere Curtici - Arad" — registrul
- `D82f19128` R A ADMINISTRATIA ZONEI LIBERE CURTICI ARAD — declaratii
### SPITALUL PNEUMOFTIZIOLOGIE (Arges)
- `G03264` SPITALUL PNEUMOFTIZIOLOGIE — registrul
- `D1ff332e6` SPITALUL DE PNEUMOFTIZIOLOGIE — declaratii
### SERVICIUL PUBLIC DE ALIMENTARE CU APA CANALIZARE SI SALUBRIZARE (Bihor)
- `D29b4b2ac` SERVICIUL PUBLIC DE ALIMENTARE CU APA CANALIZARE SI SALUBRIZARE — declaratii
- `D884ef8ee` SERVICIUL PUBLIC DE ALIMENTARE CU APA CANALIZARE SALUBRIZARE — declaratii
### Spitalul de Pneumoftiziologie Oradea (Bihor)
- `G05278` Spitalul de Pneumoftiziologie Oradea — registrul
- `G05279` SPITALUL DE PNEUMOFTIZIOLOGIE ORADEA — registrul
### CENTRUL JUDETEAN DE RESURSE SI DE ASISTENTA EDUCATIONALA (Bistrita Nasaud)
- `Ddba0f4c9` CENTRUL JUDETEAN DE RESURSE SI DE ASISTENTA EDUCATIONALA — declaratii
- `D21d92a75` CENTRUL JUDETEAN DE RESURSE SI ASISTENTA EDUCATIONALA — declaratii
### STATIUNEA DE CERCETARE-DEZVOLTARE PENTRU POMICULTURA BISTRITA (Bistrita Nasaud)
- `A3094573` STATIUNEA DE CERCETARE-DEZVOLTARE PENTRU POMICULTURA BISTRITA — anaf | declaratii; parents 4221187; Bistrita Nasaud, Municipiul Bistrita, STRADA DRUMUL DUMITREI NOU, Numa
- `G06268` Statiunea de Cercetare - Dezvoltare pentru Pomicultura Bistrita — registrul
### Directia pentru Sport a Judetului Botosani (Botosani)
- `G07231` Directia pentru Sport a Judetului Botosani — registrul
- `G07233` Directia pentru Sport a judetului Botosani — registrul
### Comisariatul Judetean al Garzii Nationale de Mediu Brasov (Brasov)
- `G09120` Comisariatul Judetean al Garzii Nationale de Mediu Brasov — registrul
- `G09121` COMISARIATUL JUDEŢEAN AL GARZII NAŢIONALE DE MEDIU BRASOV — registrul
### Complexul Sportiv National Poiana Brasov (Brasov)
- `G09151` Complexul Sportiv National Poiana Brasov — registrul
- `G09152` COMPLEXUL SPORTIV NATIONAL POIANA BRASOV — registrul
### AGENTIA DE PLATI SI INTERVENTIE PENTRU AGRICULTURA (Bucuresti)
- `G10045` AGENTIA DE PLATI SI INTERVENTIE PENTRU AGRICULTURA — registrul | declaratii
- `Df1482d5b` AGENTIA DE PLATI SI INTERVENTIE IN AGRICULTURA — declaratii
### CENTRUL NATIONAL DE CALIFICARE SI INSTRUIRE FEROVIARA - CENAFER (Bucuresti)
- `A16944447` CENTRUL NATIONAL DE CALIFICARE SI INSTRUIRE FEROVIARA - CENAFER — anaf | roepas | declaratii; parents 13633330; Bucuresti, Sectorul 1 al Municipiului Bucuresti, CALE GRIVITEI, Numar 
- `G10178` CENAFER - Centrul National de Calificare si Instruire Feroviara — registrul
### Confederatia Nationala Sindicala - "Cartel Alfa" (Bucuresti)
- `G10302` Confederatia Nationala Sindicala - "Cartel Alfa" — registrul
- `D18eed5fa` CONFEDERATIA NATIONALA SINDICALA CARTEL ALFA — declaratii
### DIRECTIA DE ASISTENTA SOCIALA (Bucuresti)
- `D0059b0fb` DIRECTIA DE ASISTENTA SOCIALA — declaratii
- `D313de646` DIRECTIA ASISTENTA SOCIALA — declaratii
### DIRECTIA DE IMPOZITE SI TAXE LOCALE (Bucuresti)
- `G10329` DIRECTIA DE IMPOZITE SI TAXE LOCALE — registrul
- `G10358` Directia Impozite si Taxe Locale — registrul
### DIRECTIA GENERALA DE EVIDENTA A PERSOANELOR BUCURESTI (Bucuresti)
- `G10350` DIRECTIA GENERALA DE EVIDENTA A PERSOANELOR BUCURESTI — registrul
- `D16854866` DIRECTIA GENERALA DE EVIDENTA PERSOANELOR BUCURESTI — declaratii
### Directia de Politie Comunitara Sector 5 (Bucuresti)
- `G10334` Directia de Politie Comunitara Sector 5 — registrul
- `G10374` DIRECTIA POLITIE COMUNITARA SECTOR 5 — registrul
### Federatia Romana de Schi Biatlon (Bucuresti)
- `R11042378` Federatia Romana de Schi Biatlon — roepas | registrul; Str.Vasile Conta, Nr.16, sector 2
- `D0098de31` FEDERATIA ROMANA SCHI BIATLON — declaratii
### INSTITUTUL DE FONOAUDIOLOGIE SI CHIRURGIE FUNCTIONALA O.R.L. PROF. DR. D. HOCIOTA (Bucuresti)
- `A4316210` INSTITUTUL DE FONOAUDIOLOGIE SI CHIRURGIE FUNCTIONALA O.R.L. PROF. DR. D. HOCIOTA — anaf | declaratii; parents 4266456; Bucuresti, Sectorul 5 al Municipiului Bucuresti, STRADA MIHAIL CIORANU
- `G10570` Institutul de Fonoaudiologie si Chirurgie Functionala - O.R.L. Prof. Dr. D. Hociota — registrul
### Institutul National de Cercetare-Dezvoltare Aerospatiala "Elie Carafoli" - I.N.C.A.S. Bucuresti (Bucuresti)
- `G10606` Institutul National de Cercetare-Dezvoltare Aerospatiala "Elie Carafoli" - I.N.C.A.S. Bucuresti — registrul
- `De8b320b2` INSTITUTUL NATIONAL DE CERCETARE DEZVOLTARE AEROSPATIALA ELIE CARAFOLI I N C A S BUCURESTI — declaratii
### RA ROMATSA (Bucuresti)
- `D25ed8061` RA ROMATSA — declaratii
- `D8c28a92b` ROMATSA RA — declaratii
### Regia Nationala a Padurilor - Romsilva (Bucuresti)
- `G10796` Regia Nationala a Padurilor - Romsilva — registrul
- `D4618737e` REGIA NATIONALA A PADURILOR ROMSILVA — registrul | declaratii
### Societatea Nationala a Sarii - SA (Bucuresti)
- `G10849` Societatea Nationala a Sarii - SA — registrul
- `Defa894f4` SOCIETATEA NATIONALA A SARII SA — declaratii
### Unitatea Militara 02433 Bucuresti (Bucuresti)
- `G10952` Unitatea Militara 02433 Bucuresti — registrul
- `G10953` Unitatea Militara 02433 Bucuresti — registrul
### APIA CJ BUZAU (Buzau)
- `D0a93d33b` APIA CJ BUZAU — declaratii
- `Dd834a07a` CJ APIA BUZAU — declaratii
### CENTRUL CULTURAL FLORICA CRISTOFOREANU RM SARAT (Buzau)
- `A5033688` CENTRUL CULTURAL FLORICA CRISTOFOREANU RM SARAT — anaf; parents 2406871; Buzau, Municipiul Rimnicu Sarat, STRADA Tudor Vladimirescu, Numar 20, 
- `D5b1dcab0` CENTRUL CULTURAL FLORICA CRISTOFOREANU RM SARAT — declaratii
### MUZEUL MUNICIPAL OCTAVIAN MOSESCU RM SARAT (Buzau)
- `A4929699` MUZEUL MUNICIPAL OCTAVIAN MOSESCU RM SARAT — anaf; parents 2406871; Buzau, Municipiul Ramnicu Sarat, STRADA PRIMAVERII, Numar 4, Bloc/Scar
- `D5bb90163` MUZEUL MUNICIPAL OCTAVIAN MOSESCU RM SARAT — declaratii
### POLITIA LOCALA A MUN. RM.SARAT (Buzau)
- `A17466766` POLITIA LOCALA A MUN. RM.SARAT — anaf; parents 2406871; Buzau, Municipiul Ramnicu Sarat, STRADA VICTORIEI, Numar 95-107, Bloc/
- `Daf63f79b` POLITIA LOCALA A MUN RM SARAT — declaratii
### SERVICIUL PUBLIC COMUNITAR LOCAL DE EVIDENTA A PERSOANELOR (Buzau)
- `D4117ede0` SERVICIUL PUBLIC COMUNITAR LOCAL DE EVIDENTA A PERSOANELOR — declaratii
- `Df4a3fdc4` SERVICIUL PUBLIC COMUNITAR LOCAL PENTRU EVIDENTA PERSOANELOR — declaratii
### SPITALUL MUNICIPAL RM. SARAT (Buzau)
- `A4697653` SPITALUL MUNICIPAL RM. SARAT — anaf; parents 2406871; Buzau, Municipiul Rimnicu Sarat, STRADA NICOLAE BALCESCU, Numar 2, Blo
- `Dfbd182da` SPITALUL MUNICIPAL RM SARAT — declaratii
### OFICIUL JUDETEAN DE CONSULTANTA AGRICOLA CALARASI (Calarasi)
- `G12162` OFICIUL JUDETEAN DE CONSULTANTA AGRICOLA CALARASI — registrul
- `G12163` Oficiul Judeţean de Consultanţă Agricolă Călăraşi — registrul
### ASOCIATIA DE STIINTE COGNITIVE DIN ROMANIA (Cluj)
- `G14020` ASOCIATIA DE STIINTE COGNITIVE DIN ROMANIA — registrul
- `G14022` ASOCIATIA DE STIINTE COGNITIVE DIN ROMANIA — registrul
### Academia Nationala de Muzica Gheorghe Dima - Cluj-Napoca (Cluj)
- `R11058949` Academia Nationala de Muzica Gheorghe Dima - Cluj-Napoca — roepas; Str. Ion I.C. Brătianu nr. 25
- `D6d8c025c` ACADEMIA NATIONALA DE MUZICA GHEORGHE DIMA DIN CLUJ NAPOCA — declaratii
### Asociatia Centrul de Initiativa pentru Mediu (Cluj)
- `G14637` Asociatia Centrul de Initiativa pentru Mediu — registrul
- `G14638` Asociatia Centrul de Initiativa pentru Mediu — registrul
### CN de Căi Ferate C.F.R. SA - Regionala de Căi Ferate Cluj (Cluj)
- `G14048` CN de Căi Ferate C.F.R. SA - Regionala de Căi Ferate Cluj — registrul
- `G14643` CN de Căi Ferate C.F.R. SA - Regionala de Căi Ferate Cluj — registrul
### Directia Regionala de Statistica Cluj (Cluj)
- `G14163` Directia Regionala de Statistica Cluj — registrul
- `G14223` Direcţia Regională de Statistică Cluj — registrul
### FILIALA DE FURNIZARE A ENERGIEI ELECTRICE"ELECTRICA FURNIZARE TRANSILVANIA NORD" S.A. (Cluj)
- `G14642` FILIALA DE FURNIZARE A ENERGIEI ELECTRICE"ELECTRICA FURNIZARE TRANSILVANIA NORD" S.A. — registrul
- `G14645` FILIALA DE FURNIZARE A ENERGIEI ELECTRICE"ELECTRICA FURNIZARE TRANSILVANIA NORD" S.A. — registrul
### Filiala de Distributie a Energiei Electrice ELECTRICA DISTRIBUTIE TRANSILVANIA NORD S.A. (Cluj)
- `G14641` Filiala de Distributie a Energiei Electrice ELECTRICA DISTRIBUTIE TRANSILVANIA NORD S.A. — registrul
- `G14644` Filiala de Distributie a Energiei Electrice ELECTRICA DISTRIBUTIE TRANSILVANIA NORD S.A. — registrul
### INSPECTORATUL DE POLITIE AL JUD. CLUJ (Cluj)
- `A4547109` INSPECTORATUL DE POLITIE AL JUD. CLUJ — anaf; parents 4267095; Cluj, Municipiul Cluj-Napoca, STRADA TRAIAN, Numar 27, Bloc/Scara , Se
- `Dc8bb08c2` INSPECTORATUL DE POLITIE AL JUD CLUJ — declaratii
### Oil Terminal s.a. - Constanta (Constanta)
- `R11049694` Oil Terminal s.a. - Constanta — roepas | declaratii; STR. CARAIMAN, NR.2
- `D57d1664b` OIL TERMINAL S A CONSTANTA — declaratii
### STATIUNEA DE CERCETARE DEZVOLTARE PENTRU POMICULTURA CONSTANTA (Constanta)
- `A2981780` STATIUNEA DE CERCETARE DEZVOLTARE PENTRU POMICULTURA CONSTANTA — anaf | declaratii; parents 4221187; Constanta, Comuna Valu lui Traian, STRADA PEPINIEREI, Numar 25, Bloc/S
- `G15356` Statiunea de Cercetare - Dezvoltare pentru Pomicultura Constanta — registrul
### Direcţia Judeţeană pentru Tineret covasna (Covasna)
- `G16080` Direcţia Judeţeană pentru Tineret covasna — registrul
- `G16082` Directia Judeteana pentru Tineret Covasna — registrul
### SPITALUL MUNICIPAL TG. SECUIESC (Covasna)
- `A4404524` SPITALUL MUNICIPAL TG. SECUIESC — anaf; parents 4201813; Covasna, Municipiul Targu Secuiesc, STRADA FABRICILOR, Numar 2A, Bloc/
- `Db76ac294` SPITALUL MUNICIPAL TG SECUIESC — declaratii
### STATIUNEA DE CERCETARE DEZVOLTARE PENTRU CARTOF TG SECUIESC (Covasna)
- `A14829298` STATIUNEA DE CERCETARE DEZVOLTARE PENTRU CARTOF TG SECUIESC — anaf; parents 4221187; Covasna, Municipiul Targu Secuiesc, STRADA ORBAN BALAZS, Numar 15, Blo
- `Dc44dd51b` STATIUNEA DE CERCETARE DEZVOLTARE PENTRU CARTOF TG SECUIESC — declaratii
### APIA - CENTRUL JUDETEAN DAMBOVITA (Dambovita)
- `G17013` APIA - CENTRUL JUDETEAN DAMBOVITA — registrul
- `Dbfac0089` APIA CENTRUL JUDETEAN DAMBOVITA — declaratii
### INSPECTORATUL DE JANDARMI JUDETEAN DAMBOVITA (Dambovita)
- `G17203` INSPECTORATUL DE JANDARMI JUDETEAN DAMBOVITA — registrul
- `G17206` Inspectoratul Judeţean de Jandarmi Dâmboviţa — registrul
### SERVICIUL PUBLIC JUDETEAN DE PAZA SI PROTECTIE DAMBOVITA (Dambovita)
- `G17345` SERVICIUL PUBLIC JUDETEAN DE PAZA SI PROTECTIE DAMBOVITA — registrul
- `G17346` SERVICIUL PUBLIC JUDEŢEAN DE PAZĂ ŞI PROTECŢIE DÂMBOVIŢA — registrul
### AGENTIA PENTRU PROTECTIA MEDIULUI DOLJ (Dolj)
- `G18009` AGENTIA PENTRU PROTECTIA MEDIULUI DOLJ — registrul
- `G18010` Agentia pentru Protectia Mediului Dolj — registrul
### APIA - Centrul judetean Dolj (Dolj)
- `A20765768` APIA - Centrul judetean Dolj — anaf | declaratii; parents 4221187; Dolj, Municipiul Craiova, BULEVARD Nicolae Titulescu, Numar 22, Bloc/S
- `G18014` APIA - CENTRUL JUDETEAN DOLJ — registrul
### AGENTIA DE PLATI SI INTERVENTIE PENTRU AGRICULTURA - CENTRU JUDETEAN GALATI (Galati)
- `A20738801` AGENTIA DE PLATI SI INTERVENTIE PENTRU AGRICULTURA - CENTRU JUDETEAN GALATI — anaf; parents 4221187; Galati, Municipiul Galati, STRADA DRAGOS VODA, Numar 13, Bloc/Scara , 
- `G19005` AGENTIA DE PLATI SI INTERVENTIE PENTRU AGRICULTURA - CENTRU JUDETEAN GALATI — registrul
### SERVICIUL PUBLIC COMUNITAR LOCAL DE EVIDENTA A PERSOANELOR (Galati)
- `D9bb1b65c` SERVICIUL PUBLIC COMUNITAR LOCAL DE EVIDENTA A PERSOANELOR — declaratii
- `D109ede9c` SERVICIUL PUBLIC COMUNITAR LOCAL PENTRU EVIDENTA PERSOANELOR — declaratii
### Directia Judeteana pentru Tineret Giurgiu (Giurgiu)
- `G20057` Directia Judeteana pentru Tineret Giurgiu — registrul
- `G20060` Directia pentru Tineret JUDETEANA GIURGIU — registrul
### CLUBUL SPORTIV PANDURII TG-JIU (Gorj)
- `A2680418` CLUBUL SPORTIV PANDURII TG-JIU — anaf; parents 4283422; Gorj, Municipiul Targu Jiu, BULEVARD CONSTANTIN BRANCUSI, Numar 6, Blo
- `D2d6b179f` CLUBUL SPORTIV PANDURII TG JIU — declaratii
### SPITALUL DE URGENTA TG CARBUNESTI (Gorj)
- `A4510266` SPITALUL DE URGENTA TG CARBUNESTI — anaf; parents 4898681; Gorj, Orasul Tirgu Carbunesti, STRADA EROILOR, Numar 51, Bloc/Scara , 
- `Dffbb9f64` SPITALUL DE URGENTA TG CARBUNESTI — declaratii
### SPITALUL JUDETEAN DE URGENTA TG-JIU (Gorj)
- `A4448067` SPITALUL JUDETEAN DE URGENTA TG-JIU — anaf | registrul; parents 4956057; Gorj, Municipiul Targu Jiu, STRADA PROGRESULUI, Numar 18, Bloc/Scara ,
- `D06f26a2e` SPITALUL JUDETEAN DE URGENTA TG JIU — declaratii
### ACADEMIA ROMANA FILIALA IASI (Iasi)
- `A4540917` ACADEMIA ROMANA FILIALA IASI — anaf | declaratii; parents 4192472; Iasi, Municipiul Iasi, BULEVARD CAROL I, Numar 8, Bloc/Scara , Sector 
- `G25002` ACADEMIA ROMANA - FILIALA IASI — registrul
### AGENTIA JUDETEANA PENTRU OCUPAREA FORTEI DE MUNCA - ILFOV (Ilfov)
- `G26002` AGENTIA JUDETEANA PENTRU OCUPAREA FORTEI DE MUNCA - ILFOV — registrul
- `Da0fede1c` AGENTIA JUDETEANA PENTRU OCUPAREA FORTEI DE MUNCA ILFOV — declaratii
### Directia Sanitara Veterinara si pentru Siguranta Alimentelor Ilfov (Ilfov)
- `G26042` Directia Sanitara Veterinara si pentru Siguranta Alimentelor Ilfov — registrul
- `G26043` DIRECTIA SANITARA VETERINARA SI PENTRU SIGURANTA ALIMENTELOR ILFOV — registrul
### Agentia de Plati si Interventie pentru Agricultura - Centrul judetean Maramures (Maramures)
- `G27001` Agentia de Plati si Interventie pentru Agricultura - Centrul judetean Maramures — registrul
- `D7d100b0e` AGENTIA DE PLATI SI INTERVENTIE PENTRU AGRICULTURA CENTRUL JUDETEAN MARAMURES — declaratii
### DIRECTIA PENTRU AGRICULTURA SI DEZVOLTARE RURALA MARAMURES (Maramures)
- `G27046` DIRECTIA PENTRU AGRICULTURA SI DEZVOLTARE RURALA MARAMURES — registrul
- `G27057` Directia pentru Agricultura şi Dezvoltare Rurala Maramureş — registrul
### SPITALUL ORASENESC STREHAIA (Mehedinti)
- `G28149` SPITALUL ORASENESC STREHAIA — registrul
- `G28150` SPITALUL ORASENESC STREHAIA — registrul
### GIMNAZIUL DE STAT MIRON NEAGU (Mures)
- `G29081` GIMNAZIUL DE STAT MIRON NEAGU — registrul
- `G29087` Gimnaziul de Stat"Miron Neagu" — registrul
### UNIVERSITATEA DE MEDICINA SI FARMACIE DIN TIRGU MURES (Mures)
- `D2b2455f7` UNIVERSITATEA DE MEDICINA SI FARMACIE DIN TIRGU MURES — declaratii
- `Df0d244a8` UNIVERSITATEA DE MEDICINA SI FARMACIE TIRGU MURES — declaratii
### UNIVERSITATEA DE MEDICINA SI FARMACIE TARGU MURES (Mures)
- `Dcf19aae6` UNIVERSITATEA DE MEDICINA SI FARMACIE TARGU MURES — declaratii
- `D1ffdc56c` UNIVERSITATEA DE MEDICINA SI FARMACIE DIN TARGU MURES — declaratii
### UNIVERSITATEA DE MEDICINA SI FARMACIE TG MURES (Mures)
- `Dfadd6216` UNIVERSITATEA DE MEDICINA SI FARMACIE TG MURES — declaratii
- `D6d6a8ee4` UNIVERSITATEA DE MEDICINA SI FARMACIE DIN TG MURES — declaratii
### CLUBUL COPIILOR - TG.NEAMT (Neamt)
- `A2614317` CLUBUL COPIILOR - TG.NEAMT — anaf; parents 13729380; Neamt, Orasul Targu Neamt, STRADA MARASESTI, Numar 101, Bloc/Scara , S
- `D94d1394a` CLUBUL COPIILOR TG NEAMT — declaratii
### ORGANISMUL INTERMEDIAR REGIONAL POS DRU - Regiunea Nord - Est (Neamt)
- `G30079` ORGANISMUL INTERMEDIAR REGIONAL POS DRU - Regiunea Nord - Est — registrul
- `D2faa583a` ORGANISMUL INTERMEDIAR REGIONAL PENTRU POS DRU REGIUNEA NORD EST — declaratii
### OFICIUL JUDETEAN PENTRU PROTECTIA CONSUMATORILOR OLT (Olt)
- `G31085` OFICIUL JUDETEAN PENTRU PROTECTIA CONSUMATORILOR OLT — registrul
- `G31086` OFICIUL JUDETEAN PENTRU PROTECTIA CONSUMATORILOR OLT — registrul
### CENTRUL DE INTEGRARE PRIN TERAPIE OCUPATIONALA PENTRU PERSOANE ADULTE CU HAN (Prahova)
- `G32027` CENTRUL DE INTEGRARE PRIN TERAPIE OCUPATIONALA PENTRU PERSOANE ADULTE CU HAN — registrul
- `G32028` CENTRUL DE INTEGRARE PRIN TERAPIE OCUPATIONALA PENTRU PERSOANE ADULTE CU HAN — registrul
### SPITALUL GENERAL C.F. PLOIESTI (Prahova)
- `G32303` SPITALUL GENERAL C.F. PLOIESTI — registrul
- `G32304` SPITALUL GENERAL C.F. PLOIESTI — registrul
### APARATUL DE SPECIALITATE A PRIMARULUI (Salaj)
- `D4399da94` APARATUL DE SPECIALITATE A PRIMARULUI — declaratii
- `D65f79c2d` APARATUL DE SPECIALITATE AL PRIMARULUI — declaratii
### ACADEMIA ROMANA FILIALA TIMISOARA (Timis)
- `A5313351` ACADEMIA ROMANA FILIALA TIMISOARA — anaf | declaratii; parents 4192472; Timis, Municipiul Timisoara, BULEVARD MIHAI VITEAZU, Numar 24, Bloc/Sc
- `G38001` ACADEMIA ROMANA - FILIALA TIMISOARA — registrul
### INSPECTORATUL TERITORIAL DE REGIM SILVIC SI DE VÂNĂTOARE TIMISOARA (Timis)
- `G38116` INSPECTORATUL TERITORIAL DE REGIM SILVIC SI DE VÂNĂTOARE TIMISOARA — registrul
- `G38124` INSPECTORATUL TERITORIAL DE REGIM SILVIC SI DE VANATOARE TIMISOARA — registrul
### OFICIUL DE AMELIORARE SI REPRODUCTIE IN ZOOTEHNIE TIMIS (Timis)
- `G38152` OFICIUL DE AMELIORARE SI REPRODUCTIE IN ZOOTEHNIE TIMIS — registrul
- `G38157` OFICIUL PENTRU AMELIORARE SI REPRODUCTIE IN ZOOTEHNIE TIMIS — registrul
### INSPECTORATUL DE JANDARMI JUDETEAN TULCEA (Tulcea)
- `G39052` INSPECTORATUL DE JANDARMI JUDETEAN TULCEA — registrul
- `G39053` INSPECTORATUL DE JANDARMI JUDETEAN TULCEA — registrul
### AGENTIA JUDETEANA PENTRU PRESTATII SOCIALE VALCEA (Valcea)
- `G40011` AGENTIA JUDETEANA PENTRU PRESTATII SOCIALE VALCEA — registrul
- `G40012` AGENŢIA JUDEŢEANA DE PRESTAŢII SOCIALE VALCEA — registrul
### AGENŢIA DE PROTECŢIA MEDIULUI VALCEA (Valcea)
- `G40001` AGENŢIA DE PROTECŢIA MEDIULUI VALCEA — registrul
- `Ddf68df82` AGENTIA PENTRU PROTECTIA MEDIULUI VALCEA — declaratii
### CLUBUL SPORTIV CHIMIA RM. VALCEA (Valcea)
- `A2541223` CLUBUL SPORTIV CHIMIA RM. VALCEA — anaf | registrul; parents 4283422; Valcea, Municipiul Ramnicu Valcea, STRADA NICOLAE BALCESCU, Numar 24, 
- `Da0592ec2` CLUBUL SPORTIV CHIMIA RM VALCEA — declaratii
### SEMINARUL TEOLOGIC ORTODOX SF.NICOLAE MUN RM.VALCEA JUDETUL VALCEA (Valcea)
- `A2540970` SEMINARUL TEOLOGIC ORTODOX SF.NICOLAE MUN RM.VALCEA JUDETUL VALCEA — anaf; parents 2540813 | 13729380; Valcea, Municipiul Ramnicu Valcea, STRADA ANTIM IVIREANUL, Numar 17, B
- `D15ab6fdc` SEMINARUL TEOLOGIC ORTODOX SF NICOLAE MUN RM VALCEA JUDETUL VALCEA — declaratii
### TEATRUL ANTON PANN RM VALCEA (Valcea)
- `A2649480` TEATRUL ANTON PANN RM VALCEA — anaf | registrul; parents 2540929; Valcea, Municipiul Ramnicu Valcea, BULEVARD TUDOR VLADIMIRESCU, Numar 
- `Dd6e23a41` TEATRUL ANTON PANN RM VALCEA — declaratii
### STATIUNEA DE CERCETARE - DEZVOLTARE PENTRU PAJISTI VASLUI (Vaslui)
- `G41112` STATIUNEA DE CERCETARE - DEZVOLTARE PENTRU PAJISTI VASLUI — registrul
- `D4e8edafd` STATIUNEA DE CERCETARE DEZVOLTARE PENTRU PAJISTI VASLUI — declaratii
