import streamlit as st
import pandas as pd
import gspread

st.set_page_config(layout="wide")



def ucitaj_podatke():
    
    podaci_računa = dict(st.secrets["gcp_service_account"])
    
    klijent = gspread.service_account_from_dict(podaci_računa)

    tablica = klijent.open("KNJIGE")
    radni_list = tablica.worksheet("knjige")

    podaci = radni_list.get_all_records()
    knjige = pd.DataFrame(podaci)

    return knjige, radni_list


knjige, radni_list = ucitaj_podatke()



if not knjige.empty: 
    knjige["Godina"] = pd.to_numeric(knjige["Godina"], errors="coerce")
    knjige["Ocjena"] = pd.to_numeric(knjige["Ocjena"], errors="coerce")

st.title("Moja kućna knjižnica")
st.subheader("Neke knjige koje posjedujem i rado čitam.")

if knjige.empty:
    st.info("U tablici još nema knjiga.")
    
else:
    st.dataframe(knjige, hide_index=True)



st.subheader("Dodaj novu knjigu")

with st.form("forma_za_dodavanje_knjige", clear_on_submit=True): 
    naslov = st.text_input("Naslov knjige:", placeholder="Primjerice: Rudnik čvaraka")
    autor = st.text_input("Autor knjige:", placeholder="Primjerice: Božidar Nagy")
    nakladnik = st.text_input("Nakladnik (izdavač) knjige:", placeholder="Primjerice: Verbum")
    mjesto = st.text_input("Mjesto izdavanja knjige:", placeholder="Primjerice: Garčin")
    godina = st.number_input("Godina izdavanja knjige:", min_value=1800, max_value=2026, value=None, placeholder="Unesite godinu.")
    vrsta = st.text_input("Vrsta knjige:", placeholder="Primjerice: roman")
    ocjena = st.slider("Ocjena knjige:", min_value=1, max_value=10, value=5)

    gumb_dodaj = st.form_submit_button("Dodaj knjigu.")

if gumb_dodaj:
    if naslov.strip() and autor.strip() and nakladnik.strip() and mjesto.strip() and godina is not None and vrsta.strip():
        novi_red = [naslov.strip(), autor.strip(), nakladnik.strip(), mjesto.strip(), int(godina), vrsta.strip(), ocjena]

        radni_list.append_row(novi_red)

        st.success("Knjiga je uspješno dodana.")
        st.rerun() 

    else:
        st.warning("Unesite naslov, autora, nakladnika, mjesto, godinu i vrstu knjige.")



st.subheader("Pretraži knjige")

if knjige.empty:
    st.info("Nema knjiga za pretraživanje.")

else:
    trazeni_autor = st.text_input("Upišite traženog autora za pretraživanje po željenom autoru:", 
                                  placeholder="Primjerice: August Šenoa"
                                  )
    trazena_godina = st.number_input("Upišite traženu godinu za pretraživanje po željenoj godini:", 
                                     min_value=1800, max_value=2026, value=None, placeholder="Primjerice: 1941"
                                     )

    filtrirane_knjige = knjige

    if trazeni_autor.strip():
        filtrirane_knjige = filtrirane_knjige[
            filtrirane_knjige["Autor"].str.contains(
                trazeni_autor.strip(),
                case=False
            )
        ]

    if trazena_godina is not None:
        filtrirane_knjige = filtrirane_knjige[filtrirane_knjige["Godina"] == int(trazena_godina)]

    if filtrirane_knjige.empty:
        st.info("Nije pronađena nijedna knjiga.")

    else: 
        st.dataframe(filtrirane_knjige, hide_index=True)



st.subheader("Brisanje knjiga")

if knjige.empty:
    st.info("Nema knjiga za brisanje.")

else: 
    def opis_knjige(indeks):
        knjiga = knjige.iloc[indeks]

        return (f"Knjiga '{knjiga['Naslov']}' čiji je autor {knjiga['Autor']} i koju je nakladnik {knjiga['Nakladnik']} " 
               f"u mjestu {knjiga['Mjesto']} objavio {int(knjiga['Godina'])}. godine je po vrsti {knjiga['Vrsta']} " 
               f"i ima ocjenu {knjiga['Ocjena']}.") 

    odabrani_indeks = st.selectbox("Odaberite knjigu za brisanje.",
                                   options=range(len(knjige)),
                                   index=None,
                                   placeholder="Odaberite jednu knjigu koju želite obrisati iz tablice.",
                                   format_func=opis_knjige
                                   )


    if st.button("Izbriši knjigu."):
        if odabrani_indeks is not None:
            redak_u_tablici =  odabrani_indeks + 2
            radni_list.delete_rows(redak_u_tablici)

            st.success("Knjiga je uspješno izbrisana.")
            st.rerun()

        else:
            st.warning("Prvo trebate odabrati knjigu za brisanje.")



st.subheader("Pet najboljih knjiga prema kriteriju ocjene (silazno sortirano)")

if knjige.empty:
    st.info("Nema nikakvih knjiga za prikaz.")

else:
    najboljih_pet = knjige.sort_values(by="Ocjena", ascending=False).head(5)

    st.dataframe(najboljih_pet, hide_index=True) 
