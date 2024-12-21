NOTES = 'C', 'D', 'E', 'F', 'G', 'A', 'B'
HALF_STEP_NOTES = 'F', 'C'


def get_scale(mode, key):
    try:
        next_key, shift_key = key
        current_shift = 1 if shift_key == '#' else -1
    except ValueError:
        next_key = key
        current_shift = 0

    result = [key]
    for scale_interval in mode.split()[: -1]:
        try:
            next_key = NOTES[NOTES.index(next_key) + 1]
        except IndexError:
            next_key = NOTES[0]

        need_interval = 2 if scale_interval == 'W' else 1
        next_key_interval = 1 if next_key in HALF_STEP_NOTES else 2

        current_shift += need_interval - next_key_interval

        if current_shift < 0:
            result.append(f'{next_key}b')
        elif current_shift > 0:
            result.append(f'{next_key}#')
        else:
            result.append(next_key)

    return result


def test1():
    assert get_scale('W W H W W W H', 'C') == ['C', 'D', 'E', 'F', 'G', 'A', 'B']  # Ionian/Major scale
    assert get_scale('W H W W W H W', 'C') == ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb']  # Dorian scale
    assert get_scale('H W W W H W W', 'C') == ['C', 'Db', 'Eb', 'F', 'G', 'Ab', 'Bb']  # Phrygian scale
    assert get_scale('W W W H W W H', 'C') == ['C', 'D', 'E', 'F#', 'G', 'A', 'B']  # Lydian scale
    assert get_scale('W W H W W H W', 'C') == ['C', 'D', 'E', 'F', 'G', 'A', 'Bb']  # Mixolydian scale
    assert get_scale('W H W W H W W', 'C') == ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb']  # Aeolian/Minor scale
    assert get_scale('H W W H W W W', 'C') == ['C', 'Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb']  # Locrian scale

    assert get_scale('W W H W W W H', 'D') == ['D', 'E', 'F#', 'G', 'A', 'B', 'C#']  # D major scale
    assert get_scale('W W H W W W H', 'E') == ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#']  # E major scale
    assert get_scale('W W H W W W H', 'F') == ['F', 'G', 'A', 'Bb', 'C', 'D', 'E']  # F major scale
    assert get_scale('W W H W W W H', 'G') == ['G', 'A', 'B', 'C', 'D', 'E', 'F#']  # G major scale
    assert get_scale('W W H W W W H', 'A') == ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#']  # A major scale
    assert get_scale('W W H W W W H', 'B') == ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#']  # B major scale

    assert get_scale('W W H W W W H', 'C#') == ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#']  # NEW
