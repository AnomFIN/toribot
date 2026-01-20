# Tori Ostobotti 💰

Erillinen botti Tori.fi "Ostetaan" -ilmoitusten seurantaan OpenAI-pohjaisella arvostuksella.

## Ominaisuudet

- 🔄 **Automaattinen hakeminen**: Tarkistaa Tori.fi:n ostoilmoitukset 5 minuutin välein (oletuksena)
- 🖼️ **Kuvien lataus**: Lataa jopa 5 kuvaa per ilmoitus
- 🤖 **OpenAI Arvostus**: Automaattinen arvostus GPT-malleilla
- ⚙️ **Web GUI**: Moderni käyttöliittymä asetuksilla
- 💾 **Pysyvä tallennus**: Kaikki tila tallennettu JSON-tiedostoihin
- 🛡️ **Vankka virheenkäsittely**: Ei kaadu, seuraa virheitä per ilmoitus
- 🌐 **Kohtelias hakeminen**: Jitter, uudelleenyritykset ja eksponentiaalinen takaperinyritys

## Pika-aloitus

### 1. Asenna riippuvuudet

```bash
pip install -r requirements.txt
```

### 2. Käynnistä Ostobotti

```bash
python3 ostobotti.py
```

### 3. Avaa GUI

Avaa http://127.0.0.1:8789 selaimessasi

## Tiedostorakenne

```
/toribot/
  ostobotti.py              # Päähakemisto-ohjelma
  ostobotti_gui.html        # Web-käyttöliittymä
  styles.css                # Tyylittely (jaettu toribot.py:n kanssa)
  requirements.txt          # Python-riippuvuudet (jaettu)
  ostobotti_products.json   # Tuotetietokanta (automaattisesti luotu)
  ostobotti_settings.json   # Asetukset (automaattisesti luotu)
  /ostobotti_debug/         # Debug-lokit (automaattisesti luotu)
  /ostobotti_images/        # Ladatut kuvat (automaattisesti luotu)
```

## Asetukset

Kaikki asetukset voidaan hallita GUI:n kautta:

### Yleiset
- **Tarkistusväli**: Kuinka usein tarkistetaan uusia ilmoituksia (oletus: 300s / 5min)
- **Pyyntöjen aikakatkaisu**: HTTP-pyyntöjen aikakatkaisu (oletus: 15s)
- **Maksimi uudelleenyritykset**: Uudelleenyritysten määrä (oletus: 2)

### Kuvat
- **Lataus käytössä**: Kytke kuvien lataus päälle/pois
- **Maksimi kuvat**: Kuvien määrä per ilmoitus (oletus: 5)

### OpenAI
- **API-avain**: OpenAI API-avaimesi (tallennetaan turvallisesti ostobotti_settings.json:iin)
- **Malli**: Käytettävä malli (oletus: gpt-4o-mini)
- **Arvostusväli**: Kuinka usein arvostukset suoritetaan (oletus: 60 min)

### Palvelin
- **Host**: Palvelimen isäntä (oletus: 127.0.0.1)
- **Portti**: Palvelimen portti (oletus: 8789)

## Käyttö

### Tuotteet-välilehti
- Tarkastele kaikkia löydettyjä ilmoituksia
- Katso kuvia, kuvauksia, sijainteja, ostajia
- Lue OpenAI-arvostukset
- Klikkaa "Näytä" avataksesi ilmoituksen Tori.fi:ssä
- Klikkaa "Suorita arvostukset" käynnistääksesi OpenAI-analyysin manuaalisesti

### Asetukset-välilehti
- Muokkaa kaikkia botin asetuksia
- Tallenna OpenAI API-avain
- Muutokset astuvat voimaan välittömästi (paitsi palvelinasetukset)

## Turvallisuusominaisuudet

- **Siisti sammutus**: Paina CTRL+C pysäyttääksesi siististi
- **Virheiden seuranta**: Jokainen ilmoitus seuraa purkamisvirheitä
- **Uudelleenyrityslogiikka**: Eksponentiaalinen takaperinyritys epäonnistuneille pyynnöille
- **Jitter**: Satunnainen 0-3s viive välttämään mallin havaitsemista
- **Tilan pysyvyys**: Kaikki tiedot tallennettu JSON-tiedostoihin
- **Ei kaatumisia**: Kattava poikkeuskäsittely

## Arkkitehtuuri

```python
# Selkeä huolien erottelu
SettingsManager      # Asetusten pysyvyys ja validointi
ProductDatabase      # Tuotetallennus säikeistä turvallisilla operaatioilla
ToriFetcher          # HTTP-pyynnöt uudelleenyrityksillä ja jitterillä
ProductExtractor     # HTML-jäsentäminen ja tietojen purkaminen
OpenAIValuator       # OpenAI API-integraatio
ToriBot              # Pääkoordinaattori taustasäikeillä
Flask App            # REST API ja GUI-palvelu
```

## API-päätepisteet

- `GET /` - Palvele GUI
- `GET /api/products` - Hae kaikki tuotteet
- `GET /api/settings` - Hae nykyiset asetukset
- `POST /api/settings` - Päivitä asetukset
- `POST /api/valuate` - Käynnistä manuaalinen arvostus
- `GET /ostobotti_images/<filename>` - Palvele ladattuja kuvia

## Erot toribot.py:stä

Ostobotti eroaa alkuperäisestä toribot.py:stä seuraavilla tavoilla:

1. **Hakee "Ostetaan" ilmoituksia**: Käyttää `trade_type=3` hakuparametria
2. **5 minuutin tarkistusväli**: Oletuksena 300 sekuntia toribot.py:n 60 sekunnin sijaan
3. **Eri portti**: Käyttää porttia 8789 toribot.py:n 8788:n sijaan
4. **Erilliset tiedostot**: Kaikki datatiedostot ovat prefiksoitu "ostobotti_" välttämään konflikteja
5. **Ostoilmoitusten arvostus**: OpenAI-prompt optimoitu ostoilmoitusten analysointiin

## Vaatimukset

- Python 3.8+
- flask >= 3.0.0
- requests >= 2.31.0
- pillow >= 10.0.0
- openai >= 1.0.0

## Lisenssi

Henkilökohtainen käyttöprojekti Tori.fi-ilmoitusten seurantaan.
