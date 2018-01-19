import MeCab
from typing import List

KATA = [chr(x) for x in range(12449, 12535)]
HIRA = [chr(x) for x in range(12353, 12439)]
KANA = KATA + HIRA
KATA_TO_HIRA = dict(zip(KATA, HIRA))
mecab = MeCab.Tagger('-Ochason')

def parse_sentence(sentence: str) -> tuple:
    parsed = mecab.parse(sentence).split()
    for item in parsed:
        yield tuple(item.split(','))


def assoc_kanji_kana(word: str, kana: str) -> list:
    assoc = [['','']]
    kana_start = 0
    for i, char in enumerate(word):
        if char in KANA:
            kana_pos = kana.find(char, i)
            kana_part = kana[kana_start:kana_pos]
            kana_start = kana_pos + 1
            assoc[-1][1] = kana_part
            assoc.append([char, ''])
            if i != (len(word) - 1):
                assoc.append(['',''])
        else:
            assoc[-1][0] += char
            if i == (len(word) - 1):
                assoc[-1][1] = kana[kana_start:]

    return assoc


def convert_to_ruby(sentence: str) -> str:
    new_sentence: List[str] = []
    for orig, kana in parse_sentence(sentence):
        if (orig == kana) or (orig == convert_to_hiragana(kana)) or (not kana):
            new_sentence.append(orig)
        else:
            assoc = assoc_kanji_kana(orig, convert_to_hiragana(kana))
            new_sentence.append('<ruby>')
            for word, yomi in assoc:
                new_sentence.append(f"<rb>{word}<rt>{yomi}")
            new_sentence.append('</ruby>')

    return ''.join(new_sentence)


def convert_to_hiragana(word: str) -> str:
    return ''.join([chr(ord(c) - 96) for c in word])


def test_convert_to_ruby():
    sample = "pythonが好きです"
    answer = "pythonが<ruby><rb>好<rt>す<rb>き<rt></ruby>です"
    assert convert_to_ruby(sample) == answer

    sample = '今日の会議'
    answer = '<ruby><rb>今日<rt>きょう</ruby>の<ruby><rb>会議<rt>かいぎ</ruby>'
    assert convert_to_ruby(sample) == answer


def test_parse_sentence():
    sample = "pythonが好きです"
    answer = [('python', ''), ('が', 'ガ'), ('好き', 'スキ'), ('です', 'デス')]
    assert list(parse_sentence(sample)) == answer


def test_convert_katakana_to_hiragana():
    for char in KATA:
        assert convert_to_hiragana(char) == KATA_TO_HIRA[char]

    assert convert_to_hiragana('ヒラガナ') == 'ひらがな'
    assert convert_to_hiragana('ギョウ') == 'ぎょう'


def test_assoc_kanji_kana():
    sample_kanji = "振り仮名"
    sample_kana = "ふりがな"
    answer = [['振','ふ'],['り',''],['仮名','がな']]

    assert assoc_kanji_kana(sample_kanji, sample_kana) == answer
