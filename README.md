# Network Scanner IP

## Opis celu programu
Program służy do prostego skanowania sieci lokalnej, aby sprawdzić jakie urządzenia są aktualnie aktywne w danej sieci. Aplikacja pokazuje adres IP urządzenia, jego status (UP/DOWN) oraz adres MAC. Można też zapisać wyniki w formacie JSON. Skrypt działa z użyciem poleceń systemowych i został napisany w Pythonie.

## Wymagania
*   **System operacyjny**: Linux.
*   **Python**: Wersja 3.6 lub nowsza.
*   **Uprawnienia**: Do poprawnego pobrania adresów MAC wymagane jest działanie w sieci lokalnej.

## Komenda scan
Główną funkcjonalnością programu jest moduł `scan`, który analizuje podaną podsieć.

**Składnia:**
python3 skanIP.py scan [ZAKRES_SIECI] [OPCJE]

## Opcje
*   **--timeout [cyfra]**: Ustawia maksymalną ilość czasu czekania na ping.
*   **--json [nazwa jsona z odpowiednim rozszerzeniem .json]**: Po skończonym skanowaniu nieprzerwanym wynik zostaje zapisany w odpowiednio nazwanym pliku json.

## Przykładowy wynik

*   **Tabela w terminalu:**
Skanowanie sieci: 192.168.1.0/24
```
NR   | ADRES IP        | STATUS | MAC
--------------------------------------------------
1    | 192.168.1.1     | UP     | 98:41:5c:3e:a2:ef
2    | 192.168.1.2     | DOWN   | -
3    | 192.168.1.3     | UP     | 70:4f:57:18:a4:c3
```

*   **Wynik w formacie JSON:**
```
     {
        "nr": 1,
        "ip": "192.168.1.1",
        "status": "UP",
        "mac": "d8:7d:7f:7f:ac:69"
    },
    {
        "nr": 2,
        "ip": "192.168.1.2",
        "status": "DOWN",
        "mac": " - "
    }
```
