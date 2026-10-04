# Uključujemo potrebne module:
import streamlit as st # Uključujemo ovaj modul jer radimo Streamlit aplikaciju.
import pandas as pd # Potreban za sortiranje. Poslije ćemo ga uzimati kao DataFrame pa nam treba.
import gspread # Potreban da se povežemo na Google račun.



def ucitaj_podatke(): # Pišemo funkciju za dohvat podataka iz naše tablice. Toj funkciji ništa ne prosljeđujemo.
    podaci_računa = dict(st.secrets["gcp_service_account"]) # Prvo želimo povući tajne podatke o našem Google računu. Pomoću 'dict' te podatke ('st.secrets') iz datoteke 'secrets.toml' pretvaramo u rječnik jer funkcija u sljedećem redu (koja će primiti te podatke) očekuje da su ti podaci u obliku rječnika. U dio 'gcp_service_account' ćemo kopirati te osjetljive podatke koje će pretvoriti u rječnik.
    klijent = gspread.service_account_from_dict(podaci_računa) # Pravimo klijenta (objekt) koji će se spajati na tu našu tablicu (bazu) i tamo nešto moći raditi. Funkciji 'service_account_from_dict' prosljeđujemo podatke računa. Ona će od tih podataka napraviti klijenta (objekt) koji će se spojiti na tablicu i uređivati.

    tablica = klijent.open("KNJIGE") # Otvaramo tablicu pomoću metode 'open'. Koristimo klijenta (objekt) koji se može spojiti na tablicu.
    radni_list = tablica.worksheet("knjige") # Otvaramo radni list 'knjige' iz varijable 'tablica'.

    podaci = radni_list.get_all_records() # U varijablu 'podaci' želimo dohvatiti sve podatke iz tablice. Metoda 'get_all_records' u varijablu 'podaci' će dohvatiti sve iz radnog lista osim zaglavlja. 
    knjige = pd.DataFrame(podaci) # Od podataka pravimo DataFrame (kao neka tablica koju je lakše sortirati i izdvajati iz nje). U zgaradi piše od kojih podataka (varijabla 'podaci') pravimo DataFrame i to se sprema u varijablu 'knjige'.

    return knjige, radni_list # Funkcija treba vraćati DataFrame koji je u varijabli 'knjige' i vraćati radni list u kojem su upisani podaci u varijabli 'radni_list'.

knjige, radni_list = ucitaj_podatke() # Pozovemo funkciju i želimo da nam raspakira to što povuče u dvije varijable. Vratit će n-torku koju će raspakirati na varijable 'knjige' i 'radni_list'.



# Prikaz knjiga: Prikaz podataka iz naše tablice.
# Provjeravamo je li DataFrame 'knjige' prazan. Ako je prazan, ne treba ništa pripremati ni raditi ni prikazivati.
if not knjige.empty: # Ako nije prazan, DataFrame (ima knjiga), onda godine i ocjene pretvaramo u brojeve. (To trenutno već izgledaju kao brojevi, ali to neće biti brojevi kad te podatke povuče.) Trebaju postati brojevi jer ćemo to sortirati.
    knjige["Godina"] = pd.to_numeric(knjige["Godina"], errors="coerce") # Neka uzme stupac 'Godina' i pretvori u broj. Ako negdje naiđe na neki 'string' (nema broja), inače bi se program srušio, ali pomoću korištenja 'errors' program se neće srušiti, već će samo staviti 'None' tamo gdje nije neki broj, odnosno što ne može pretvoriti u broj.
    knjige["Ocjena"] = pd.to_numeric(knjige["Ocjena"], errors="coerce") # Neka uzme stupac 'Ocjena' i pretvori u broj. 

st.title("Moja kućna knjižnica") # Postavljamo naslov.
st.subheader("Neke knjige koje posjedujem i rado čitam.") # Postavljamo podnaslov.

if knjige.empty: # Prije prikaza knjiga želimo provjeriti ima li uopće knjiga u DataFrameu.
    st.info("U tablici još nema knjiga.") # Ako nema knjiga (prazan DateaFrame), onda ispisuje informativnu poruku plave boje.
else:
    st.dataframe(knjige, hide_index=True) # Inače ako ima knjiga, onda 'streamlit dataframe' uzme knjige (dataframe knjige) i od njih napravi svoj 'dataframe' koji će lijepo izgledati u njegovom prikazu, tj. 'streamlit aplikaciji'. Ako nemamo 'hide_index=True', onda bi nam 'pandas' pravio svoj dodatni stupac s nekim svojim indeksima, a to je bespotrebno.



# Dodavanje knjiga: Dodajmo nekoliko knjiga u našu tablicu.
st.subheader("Dodaj novu knjigu")

with st.form("forma_za_dodavanje_knjige", clear_on_submit=True): # Pravimo obrazac za dodavanje knjiga. Unutar zagrade mu dajemo neki naziv koji nama neće nigdje trebati, ali 'streamlitu' treba da svaki obrazac ima svoj jedinstven naziv. Ako želimo da se polja očiste nakon unosa, onda postavljamo parametar 'clear_on_submit' na 'True'.
    naslov = st.text_input("Naslov knjige:") # Sve napisano uvučeno je dio tog obrasca. Želimo da korisnik upiše naslov knjige.
    autor = st.text_input("Autor knjige:")
    nakladnik = st.text_input("Nakladnik (izdavač) knjige:")
    mjesto = st.text_input("Mjesto izdavanja knjige:")
    godina = st.number_input("Godina izdavanja knjige:", min_value=1800, max_value=2026, value=None, placeholder="Unesite godinu.") # Početnu vrijednost za unesenu godinu postavljamo na 'None' jer ćemo kasnije provjeravati je li nešto upisano u tom polju. Ako nema ništa upisano ('None'), onda nećemo moći ništa dodati jer nismo sve unijeli. 'placeholder' je tekst koji će pisati u polju da bude jasno što tu treba upisati (kad kliknemo na polje i krenemo upisivati, automatski će se obrisati taj pomoćni tekst u polju).
    vrsta = st.text_input("Vrsta knjige:")
    ocjena = st.slider("Ocjena knjige:", min_value=1, max_value=10, value=5) # 'slider' je klizač. 'value' je početno postavljena ocjena dok ne odaberemo neku drugu.

    gumb_dodaj = st.form_submit_button("Dodaj knjigu") # Kod ovih obrazaca ne rade klasični (obični) gumbi koje smo prije koristili ('button'), već moramo imati posebne gumbe.

if gumb_dodaj: # Kad se stisne gumb 'Dodaj knjigu', onda prvo želimo provjeriti je li korisnik upisao naslov, autora, nakladnika, mjesto, godinu i vrstu knjige. Za ocjenu ne provjerava jer je na klizaču (ne upisuje je) i automatski je ponuđena ocjena (početna vrijednost) 5 koja će vrijediti ako korisnik ništa ne odabere.
    if naslov.strip() and autor.strip() and nakladnik.strip() and mjesto.strip() and godina is not None and vrsta.strip(): # 'strip' uklanja razmake (prazni znak, razmaknica) i dodatne posebne znakove na početku i na kraju 'stringa'. 'Ako je neki tekst upisan u naslov, autora, nakladnika, mjesto, godinu i vrstu, onda od tih šest unesenih stvari treba napraviti listu 'novi_red'.
        novi_red = [naslov.strip(), autor.strip(), nakladnik.strip(), mjesto.strip(), int(godina), vrsta.strip(), ocjena] # Pomoću 'strip' uklanjamo razmake (ako imaju prije i poslije). Godinu šaljemo kao cijeli broj.

        radni_list.append_row(novi_red) # To treba dodati u radni list 'knjige'. Metoda 'append_row' će na kraj radnog lista dodati listu. 

        st.success("Knjiga je uspješno dodana.") # To je poruka o uspješnom dodavanju.
        st.rerun() # Ako korisnik doda neku knjigu, želimo da ta knjiga odmah postane vidljiva. To postižemo tako da se pomoću 'st.rerun()' ponovno pokrene aplikacija, odnosno da se sve to osvježi.

        # Ako je sve to uneseno, onda će se svi ti unesnei podaci dodati (pomoću 'append_row') u radni list.
    else:
        st.warning("Unesite naslov, autora, nakladnika, mjesto, godinu i vrstu knjige.") # Ako nije sve to upisano, ispisuje žutu poruku upozorenja.



# Pretraživanje knjiga: Omogućimo pretraživanje knjiga po autoru i godini.

st.subheader("Pretraži knjige")

if knjige.empty: # Provjeravamo je li DataFrame 'knjige' prazan. Ako je prazan, neka se ispiše info poruka upozorenja.
    st.info("Nema knjiga za pretraživanje.")

else:
    trazeni_autor = st.text_input("Upišite autora:") # Ako ima knjiga, onda pitamo korisnika da upiše nekog autora kojeg pretražuje.
    trazena_godina = st.number_input("Upišite godinu:", min_value=1800, max_value=2026, value=None) # Ako korisnik želi pretraživati po godini.

    filtrirane_knjige = knjige # Sav sadržaj koji imamo u DateFrame 'knjige' smo kopirali u novi DateFrame 'filtrirane_knjige'. Kad filtriramo po nekom kriteriju, dobit ćemo novi DataFrame u kojem će biti samo neki podaci koje je korisnik tražio (samo knjiga željenog autora ili napisana određene godine).

    if trazeni_autor.strip(): # Ako je korisnik upisao pretraživanje samo traženog autora. Pomoću 'strip' uklanjamo suvišne razmake (prije ili poslije upisanog ili ako se upisano sastoji samo od razmaka pa se to neće prihvatiti).
        filtrirane_knjige = filtrirane_knjige[
            filtrirane_knjige["Autor"].str.contains(
                trazeni_autor.strip(),
                case=False
            )
        ] # Moramo dobiti neke nove vrijednosti u novom DateFrameu 'filtrirane_knjige'. Naredbama kažemo da uzme DateFrame 'filtrirane_knjige' u kojem se nalaze sve izvorne knjige (još ništa nije filtrirano). U uglatoj zagradi pišemo koji stupac treba gledati ako je korisnik napisao da treba pretraživati po autoru.
# 'str.contains' Kad korisnik nešto upiše, onda 'contains' pretražuje pojavljuje li se negdje u nazivu ta upisana riječ (ne traži posve točna podudaranja). Pretražuje pojavljuje li se ono što je upisano u varijabli 'traženi_autor'. Pomoću 'strip' uklanjamo razmake da ne ovisimo o njima. Parametar 'case=False' služi da ne ovisimo o velikim i malim slovima.

    if trazena_godina is not None: # Ako korisnik upiše neku traženu godinu.
        filtrirane_knjige = filtrirane_knjige[filtrirane_knjige["Godina"] == int(trazena_godina)] # U DataFrame gleda stupac 'godina'. Kad naiđe na godinu koja je jednaka traženoj upisanoj godini (pomoću 'int' pretvorena u cijeli broj), onda će izbaciti knjige nastale tijekom te upisane godine.

    if filtrirane_knjige.empty: # Ako je korisnik upisao nepostojećeg autora ili nepostojeću godinu (tijekom koje nije izdana nijedna navedena knjiga), onda će 'filtrirane_knjige' biti prazno pa će se ispisati info poruka.
        st.info("Nije pronađena nijedna knjiga.")

    else: 
        st.dataframe(filtrirane_knjige, hide_index=True) # Inače ako je ipak našao nešto, onda neka napravi streamlit DataFrame, ali ne od 'knjige', već od 'filtrirane_knjige'. Na kraju napišemo da ne pravi bespotrebni stupac s indeksima.



# Brisanje knjiga: Obrišimo neku knjigu iz naše tablice.

st.subheader("Brisanje knjiga")

if knjige.empty:
    st.info("Nema knjiga za brisanje.")
else: # Briše ako ima knjiga za brisanje. Prije smo brisali pomoću indeksa, ali to nije najbolje radilo, već je izbacivalo oznake redova i indeksa. Sada ćemo to riješiti na drugačiji način. Pomoću toga da se u padajućem izborniku izlistaju postojeće knjige pa da korisnik odabere jednu knjigu koju će obrisati pomoću gumba 'Obriši'.
    def opis_knjige(indeks): # Definiramo funkciju 'opis_knjige' kojoj će se proslijediti indeks knjige zato što će u tom padajućem izborniku raditi s indeksima (brojevima). Budući da ne želimo da se korisniku tu pokazuju brojevi 1, 2, 3... jer ne zna što briše, onda će ta funkcija taj indeks pretvoriti u opis knjige (naziv, godina...).
        knjiga = knjige.iloc[indeks] # Da dohvatimo u varijablu 'knjiga' iz DateFramea 'knjige' treba nam metoda 'iloc' kojoj će se proslijediti taj indeks i u varijablu 'knjiga' će vratiti sve vrijednosti koje su na tom indeksu (naslov, autor, nakladnik, mjesto, godina, vrsta, ocjena).

        return(f"Knjiga '{knjiga['Naslov']}' čiji je autor {knjiga['Autor']} i koju je nakladnik {knjiga['Nakladnik']} u mjestu {knjiga['Mjesto']} objavio {int(knjiga['Godina'])}. godine je po vrsti {knjiga['Vrsta']} i ima ocjenu {knjiga['Ocjena']}.") # Funkcija pomoću return vraća opis knjige. Dohvaća se što piše u poljima 'Naslov', 'Autor', 'Nakladnik', 'Mjesto', 'Godina', 'Vrsta' i 'Ocjena'.

    odabrani_indeks = st.selectbox("Odaberite knjigu za brisanje.",
                                   options=range(len(knjige)),
                                   index=None,
                                   placeholder="Odaberite jednu knjigu",
                                   format_func=opis_knjige
                                   ) 

# Pomoću 'selectbox' pravimo padajući izbornik. 
# Pomoću varijable 'odabrani_indeks' znamo što je korisnik odabrao. 
# Pomoću 'options' nudimo mogućnosti (opcije) koje će korisnik moći odabrati (biti mu na raspolaganje) za brisanje. Napravit će listu (točnije generator) od 0 do X. knjiga (koliko već ima knjiga). 
# 'len' će vratiti broj (n) knjiga, a 'range' će od tog broja napraviti 0, 1, 2, n-1. To će biti opcije ponuđene korisniku za brisanje. 
# Mi ne želimo da se prikazuju ti brojevi, nego ćemo te brojeve proslijediti funkciji koja nam neće vratiti broj, već cjelokupni opis knjige. 
# 'index=None' znači da ništa nije unaprijed odabrano. 
# 'placeholder' ispisuje korisniku da nije odabrana nijedna knjiga, već da mu piše tekst 'Odaberite jednu knjigu'.
# Parametar 'format_func' služi za povezivanje s funkcijom 'opis_knjige'. Dakle, kad korisnik odabere jednu od ponuđenih vrijednosti (0, 1, 2..., n-1), taj odabrani broj će se proslijediti funkciji 'opis_knjige'. Ona će uzeti taj broj i vratiti što u tom redu (na tom indeksu) konkretno piše (naslov, autor, nakladnik, mjesto, godina, vrsta, ocjena).

    # Kad korisnik gore odabere neku knjigu, onda će (dolje) stisnuti gumb za brisanje knjige. Oblikujemo taj gumb.
    if st.button("Izbriši knjigu."):
        if odabrani_indeks is not None: # Provjeramo je li nešto odabrano. U početku je kod knjiga indeks postavljen na 'None', odnosno u početku nije ništa odabrano. Ako korisnik nije ništa odabrao za brisanje, a kliknuo je gumb za brisanje knjige, logično je da ne može ništa obrisati.
            redak_u_tablici =  odabrani_indeks + 2 # Pravimo novu varijablu 'redak_u_tablici'. To je redak koji će se obrisati. U pandas DataFrameu indeksi kreću od 0 i u njemu ne postoji zaglavlje. U našoj tablici (bazi) indeksi kreću od 1 i postoji zaglavlje. Prva knjiga je u tablici (baza u Google Sheetsu) na indeksu 2 (zaglavlje je na indeksu 1). U pandas DataFrameu je prva knjiga na indeksu 0. Stoga odabrani indeks povećavamo za 2.
            radni_list.delete_rows(redak_u_tablici) # Naređujemo da uzme 'radni_list' i iskoristi metodu 'delete_rows' za brisanje redova, točnije brisanje reda 'redak_u_tablici'.

            st.success("Knjiga je uspješno izbrisana.")
            st.rerun() # Ako korisnik obriše neku knjigu, želimo da ta knjiga više ne bude vidljiva u padajućem izborniku (da je više nema, odnosno da se više ne vidi). To postižemo tako da se pomoću 'st.rerun()' ponovno pokrene aplikacija, odnosno da se sve to osvježi.

        else:
            st.warning("Prvo trebate odabrati knjigu za brisanje.") # Ako korisnik nije odabrao nikakvu knjigu, a stisnuo je gumb za brisanje knjige, onda tu treba napraviti 'warning'.



# Najbolje knjige: Prikažimo najboljih pet knjiga po ocjeni.

st.subheader("Najboljih pet knjiga po ocjeni") # To je podnaslov.

if knjige.empty:
    st.info("Nema nikakvih knjiga za prikaz.")

else:
    najboljih_pet = knjige.sort_values(by="Ocjena", ascending=False).head(5) # Ako ima knjiga, onda uzima DataFrame 'knjige' i pomoću metode 'sort_values' za sortiranje po kriteriju (stupac) 'Ocjena'.
    # Općenito, kad sortira, ako mu ne kažemo drugačije, on će automatski sam sortirati od najmanje prema najvećoj vrijednosti.
    # Budući da u ovom slučaju želimo sortirati od najveće prema najmanjoj ocjeni, upisujemo 'ascending=False'. Ako mu ne kažemo drugačije, onda će inače biti 'False'.
    # 'head(5) znači da želimo prikaz najboljih 5 knjiga.

    st.dataframe(najboljih_pet, hide_index=True) # Pravimo novi streamlit dataframe od dataframe 'najboljih_pet'. Opet skrivamo stupac s indeksima.
