# Программа, для извлечения из файла со всеми русскими существительными
# леммы для нарицательных существительных из 5 буквы

import pymorphy3
morph = pymorphy3.MorphAnalyzer()


with open('summary.txt', 'r', encoding='utf-8') as file:
    words = set([line.rstrip() for line in file.readlines()])
with open('words.txt', 'w', encoding='utf-8') as file:
    nouns = []
    for word in words:
        if not word[0].isupper():
            parsed_word = morph.parse(word)[0]
            if parsed_word.tag.POS == 'NOUN' and 'nomn' in parsed_word.tag:
                nouns.append(parsed_word.normal_form)
    print(*[noun for noun in nouns if len(noun) == 5], file=file, sep='\n')
