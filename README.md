This python script takes care of renaming TV series. 


tttt@zzzz:~/kkkk/Fallout$ python3 tvrenamer3.py 
usage: tvrenamer3.py [-h] [--execute] [--format {standard,plex,simple,minimal,kodi}] [--recursive] [--language {it,en,es,fr,de}] [--interface {it,en}]
                     [--tmdb-key TMDB_KEY] [--version] [--license]
                     directory
tvrenamer3.py: error: the following arguments are required: directory
andres@debminis:~/SerieTVArchivio/Fallout$ 

---

(not all is working.. but is enough)


zzz@tttt:~/xxx/Fallout$ python3 tvrenamer3.py . --tmdb-key xxxxxx-xxx-xxx--xxx     ** pay attention to the dot .**  , the script is working in this directory
📺 Universal TV Series Renamer v1.0
👨‍💻 Sviluppato da: Andres Zanzani
📄 Licenza: GPL-3.0
==================================================
📁 Directory: /xxx/yyyy/zzzz/Fallout
🎨 Formato: standard
🌍 Lingua: it
🔄 Ricorsivo: No
⚙️  Modalità: PREVIEW    ** PREVIEW!!! ** no change unless --execute is passed in commandline!!!
==================================================
✅ TMDB API key configurata

🌍 Scegli la lingua per i titoli degli episodi:
1. Italiano (it)
2. English (en)
3. Español (es)
4. Français (fr)
5. Deutsch (de)
Scegli lingua (1-5, o premi Enter per italiano): 

Scegli lingua (1-5, o premi Enter per italiano): 2
✅ Lingua selezionata: English
❌ Errore autenticazione TheTVDB: 401
🔄 TheTVDB non disponibile, continuo con altre fonti

📁 Trovati 8 file video
📊 Rilevate 1 serie diverse

================================================================================
📺 SERIE: Fallout (8 file)
================================================================================

🔍 Ricerca in corso per: 'Fallout'
🔄 Ricerca su TMDB...

🔍 Risultati di ricerca per: 'Fallout'
================================================================================
 1. TMDB | Fallout | 2024 | ⭐ 8.3/10
    └─ The story of haves and have-nots in a world in which there’s almost nothing left to have. 200 years ...

 2. TMDB | Fallout: Nuka Break | 2011 | ⭐ 7.7/10
 3. TMDB | Fallout: The Wanderer | 2017 | ⭐ 8.0/10
    └─ This origin story follows the not-so-NCR Ranger, James Eldridge in the Wasteland, and his first enco...

0. ❌ Nessuna delle opzioni sopra
r. 🔄 Ricerca con nome diverso
q. 🚪 Esci dal programma
Seleziona (1-3, 0, r, q): 1

==========================================================================================================================================================================
📋 PREVIEW - 8 file
==========================================================================================================================================================================
NOME ORIGINALE                                                                       | NUOVO NOME                           
-------------------------------------------------------------------------------------+--------------------------------------
Fallout.S01E01.La.fine.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv      | Fallout - [01x01] - The End.mkv      
Fallout.S01E02.L.obiettivo.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv  | Fallout - [01x02] - The Target.mkv   
Fallout.S01E03.La.testa.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv     | Fallout - [01x03] - The Head.mkv     
Fallout.S01E04.Il.Ghoul.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv     | Fallout - [01x04] - The Ghouls.mkv   
Fallout.S01E05.Il.passato.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv   | Fallout - [01x05] - The Past.mkv     
Fallout.S01E06.La.Trappola.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv  | Fallout - [01x06] - The Trap.mkv     
Fallout.S01E07.La.Radio.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv     | Fallout - [01x07] - The Radio.mkv    
Fallout.S01E08.Il.principio.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv | Fallout - [01x08] - The Beginning.mkv
-------------------------------------------------------------------------------------+--------------------------------------
📊 RISULTATI: ✅ 8 successi, ❌ 0 errori

💡 Per eseguire realmente le rinomine, aggiungi --execute
xxx@tttt:~/zzz/Fallout$ 

----

*** and this is real! ***

zzz@ttt:~/kkkk/Fallout$ python3 --interface en --language en . --tmdb-key zzzzz-zzxxxx-xxxx --execute
📺 Universal TV Series Renamer v1.0
👨‍💻 Developed by: Andres Zanzani
📄 License: GPL-3.0
==================================================
📁 Directory: /home/andres/SerieTVArchivio/Fallout
🎨 Format: standard
🌍 Episode language: en
🗣️ Interface language: en
🔄 Recursive: No
⚙️  Mode: EXECUTION
==================================================
✅ TMDB API key configured
❌ TheTVDB authentication error: 401
🔄 TheTVDB not available, continuing with other sources

📁 Trovati 8 file video
📊 Rilevate 1 serie diverse

================================================================================
📺 SERIE: Fallout (8 file)
================================================================================

🔍 Searching for: 'Fallout'
🔄 Searching TMDB...

🔍 Search results for: 'Fallout'
================================================================================
 1. TMDB | Fallout | 2024 | ⭐ 8.3/10
    └─ The story of haves and have-nots in a world in which there’s almost nothing left to have. 200 years ...

 2. TMDB | Fallout: Nuka Break | 2011 | ⭐ 7.7/10
 3. TMDB | Fallout: The Wanderer | 2017 | ⭐ 8.0/10
    └─ This origin story follows the not-so-NCR Ranger, James Eldridge in the Wasteland, and his first enco...

0. ❌ None of the above options
r. 🔄 Search with different name
q. 🚪 Exit program
Select (1-3, 0, r, q):1

🎨 Scegli il formato del nome file:
1. STANDARD: Serie - [01x01] - Episodio.mkv
2. PLEX: Serie - S01E01 - Episodio.mkv
3. SIMPLE: Serie 1x01 Episodio.mkv
4. MINIMAL: Serie S01E01.mkv
5. KODI: Serie S01E01 Episodio.mkv
Scegli formato (1-5): 1
✅ Formato selezionato: standard

⚠️  WARNING: Rename 8 files?
Confirm? [y/N]:y

==========================================================================================================================================================================
📋 EXECUTION - 8 files
==========================================================================================================================================================================
ORIGINAL NAME                                                                        | NEW NAME                             
-------------------------------------------------------------------------------------+--------------------------------------
Fallout.S01E01.La.fine.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv      | Fallout - [01x01] - The End.mkv      
Fallout.S01E02.L.obiettivo.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv  | Fallout - [01x02] - The Target.mkv   
Fallout.S01E03.La.testa.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv     | Fallout - [01x03] - The Head.mkv     
Fallout.S01E04.Il.Ghoul.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv     | Fallout - [01x04] - The Ghouls.mkv   
Fallout.S01E05.Il.passato.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv   | Fallout - [01x05] - The Past.mkv     
Fallout.S01E06.La.Trappola.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv  | Fallout - [01x06] - The Trap.mkv     
Fallout.S01E07.La.Radio.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv     | Fallout - [01x07] - The Radio.mkv    
Fallout.S01E08.Il.principio.ITA.ENG.2160p.AMZN.WEB-DL.DDP5.1.DV.HDR.H.265-MeM.GP.mkv | Fallout - [01x08] - The Beginning.mkv
-------------------------------------------------------------------------------------+--------------------------------------
📊 RESULTS: ✅ 8 successes, ❌ 0 errors
✅ Rollback script generated: rollback_renamer.py
💡 **To restore original names, run**:
   python3 "rollback_renamer.py"
   oppure: ./rollback_renamer.py
zzz@tttt:~/kkkkk/Fallout$ 

xxxx@tttt:~/ffff/Fallout$ ls
                                      'Fallout - [01x03] - The Head.mkv'    'Fallout - [01x06] - The Trap.mkv'        rollback_renamer.py
'Fallout - [01x01] - The End.mkv'     'Fallout - [01x04] - The Ghouls.mkv'  'Fallout - [01x07] - The Radio.mkv'
'Fallout - [01x02] - The Target.mkv'  'Fallout - [01x05] - The Past.mkv'    'Fallout - [01x08] - The Beginning.mkv'
xxxx@tttt:~/zzzz/Fallout$ 


(well not all in in english.. pardon me)


