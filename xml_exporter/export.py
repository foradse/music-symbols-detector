from music21 import *
import os

def MusicXML_Exporter(Data_note):

    """Сортировка нот по X координате"""
    Sort_data_note=sorted(Data_note, key=lambda x: x[1][0], reverse=False)

    s = stream.Stream()

    """Добавление методанных"""
    s.insert(0, metadata.Metadata())
    s.metadata.title = "NO TITLE"
    s.metadata.composer = "NO COMPOSER"

    # """Добавляем ключ"""
    # dict_key={"clef_g":clef.TrebleClef(),"clef_f":clef.BassClef(),"clef_c":clef.AltoClef()}
    # clif=0
    # for simbol in Sort_data_note:
    #     if simbol[0] in dict_key:
    #         clif=dict_key[simbol[0]]
    #         Sort_data_note.remove(simbol)
    # s.append(clif)

    """Добовляем тактовый размер"""
    Takt_time_in_music21=['2/2','2/4','3/2','3/4','3/8','4/4','6/8','9/8','common']
    Takt_time=['time_2_2','time_2_4','time_3_2','time_3_4','time_3_8','time_4_4','time_6_8','time_9_8','time_common']
    time=0
    for simbol in Sort_data_note:
        if simbol[0] in Takt_time:
            time=simbol[0]
            Sort_data_note.remove(simbol)
    s.append(meter.TimeSignature(Takt_time_in_music21[Takt_time.index(time)]))



    """Добавляем ноты, знаки альтерации"""
    for element_type, (x, y, width, height) in Sort_data_note:
        # Обработка ключей
        if element_type == 'clef_g':
            s.append(clef.TrebleClef())
        elif element_type == 'clef_f':
            s.append(clef.BassClef())
        elif element_type == 'clef_c':
            s.append(clef.AltoClef())

        # Обработка нот
        elif element_type.startswith('note_'):
            duration_type = element_type.split('_')[1]
            note_name = element_type.split('_')[2] if len(element_type.split('_')) > 2 else 'C'
            accidental = element_type.split('_')[3] if len(element_type.split('_')) > 3 else None

            # Создаем ноту
            n = note.Note(note_name.upper())

            # Устанавливаем длительность
            if duration_type == 'whole':
                n.duration.type = 'whole'
            elif duration_type == 'half':
                n.duration.type = 'half'
            elif duration_type == 'quarter':
                n.duration.type = 'quarter'
            elif duration_type == 'eighth':
                n.duration.type = 'eighth'

            # Устанавливаем знак альтерации
            if accidental == 'sharp':
                n.pitch.accidental = pitch.Accidental('sharp')
            elif accidental == 'flat':
                n.pitch.accidental = pitch.Accidental('flat')
            elif accidental == 'natural':
                n.pitch.accidental = pitch.Accidental('natural')

            s.append(n)

        # Обработка пауз
        elif element_type.startswith('rest_'):
            duration_type = element_type.split('_')[1]

            r = note.Rest()

            if duration_type == 'whole':
                r.duration.type = 'whole'
            elif duration_type == 'half':
                r.duration.type = 'half'
            elif duration_type == 'quarter':
                r.duration.type = 'quarter'
            elif duration_type == 'eighth':
                r.duration.type = 'eighth'

            s.append(r)

    s.write('musicxml', fp="example.musicxml")











example_notes = [
        ('time_2_2', (1, 2, 3, 6)),
        ('clef_g', (10, 20, 30, 60)),
        ('note_quarter_C', (102, 38, 20, 20)),
        ('note_eighth_D_sharp', (150, 38, 20, 20)),
        ('note_half_E_flat', (180, 38, 20, 20)),
        ('rest_quarter', (200, 50, 15, 15)),
        ('note_quarter_F_natural', (230, 38, 20, 20))
    ]

MusicXML_Exporter(example_notes)