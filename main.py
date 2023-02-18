from sound_change_rule import SoundChangeRule
from sound import Sound
from language import Language
import db
from word_form_rule import WordFormRule


def generate_koa():
    koa_sounds = list()

    koa_a = Sound('a', 'ä', 'V', 17)
    koa_sounds.append(koa_a)
    koa_e = Sound('e', 'e', 'V', 6)
    koa_sounds.append(koa_e)
    koa_i = Sound('i', 'i', 'V', 8)
    koa_sounds.append(koa_i)
    koa_o = Sound('o', 'o̞', 'V', 4)
    koa_sounds.append(koa_o)
    koa_u = Sound('u', 'ʊ', 'Vu', 7)
    koa_sounds.append(koa_u)

    koa_p = Sound('p', 'p', 'SOC', 0.7)
    koa_sounds.append(koa_p)
    koa_t = Sound('t', 't', 'SOC', 4)
    koa_sounds.append(koa_t)
    koa_k = Sound('k', 'k', 'SOC', 4.5)
    koa_sounds.append(koa_k)
    koa_q = Sound('q', 'q', 'SOC', 1)
    koa_sounds.append(koa_q)
    koa_glottalstop = Sound("'", 'ʔ', 'SOC', 5)
    koa_sounds.append(koa_glottalstop)
    koa_b = Sound('b', 'ɓ', 'SOC', 3)
    koa_sounds.append(koa_b)
    koa_tejective = Sound("t'", 't’', 'SOEC', 0.4)
    koa_sounds.append(koa_tejective)
    koa_kejective = Sound("k'", 'k’', 'SOEC', 1)
    koa_sounds.append(koa_kejective)

    koa_c = Sound('c', 't͡s', 'AOC', 1.5)
    koa_sounds.append(koa_c)
    koa_cejective = Sound("c'", 't͡sʼ', 'AOEC', 0.3)
    koa_sounds.append(koa_cejective)
    koa_ch = Sound('ch', 't͡ʃ', 'AOC', 1)
    koa_sounds.append(koa_ch)
    koa_chejective = Sound("ch'", 't͡ʃʼ', 'AOEC', 0.2)
    koa_sounds.append(koa_chejective)
    koa_ckh = Sound('ckh', 'q͡χ', 'AOC', 0.6)
    koa_sounds.append(koa_ckh)
    koa_ckhejective = Sound("ckh'", 'q͡χ’', 'AOEC', 0.125)
    koa_sounds.append(koa_ckhejective)

    koa_s = Sound('s', 's', 'FOC', 2)
    koa_sounds.append(koa_s)
    koa_x = Sound('x', 'ɬ', 'FOC', 1.75)
    koa_sounds.append(koa_x)
    koa_sh = Sound('sh', 'ʃ', 'FOC', 0.4)
    koa_sounds.append(koa_sh)
    koa_kh = Sound('kh', 'χ', 'FOC', 2.75)
    koa_sounds.append(koa_kh)
    koa_h = Sound('h', 'h', 'FOC', 1)
    koa_sounds.append(koa_h)

    koa_m = Sound('m', 'm', 'NC', 3)
    koa_sounds.append(koa_m)
    koa_n = Sound('n', 'n', 'NC', 4)
    koa_sounds.append(koa_n)

    koa_r = Sound('r', 'ɾ', 'LJC', 3)
    koa_sounds.append(koa_r)
    koa_l = Sound('l', 'l', 'LJC', 9)
    koa_sounds.append(koa_l)
    koa_y = Sound('y', 'ʎ', 'LJC', 2)
    koa_sounds.append(koa_y)

    koa_j = Sound('j', 'j', 'WJC', 3)
    koa_sounds.append(koa_j)
    koa_w = Sound('w', 'w', 'WJC', 1.25)
    koa_sounds.append(koa_w)

    koa_tj = Sound('tj', 'tʲ', 'SOC')
    koa_tjejective = Sound("tj'", 'tʲ’', 'SOEC')
    koa_ng = Sound('ng', 'ŋ', 'NC')

    koa_tactics = '{O,N}(2VJ)V(4{O,N})'

    koa_language = Language("Ko'a", koa_sounds, koa_tactics)

    plural = WordFormRule('Plural', 'N')
    plural.add_suffix_rule([koa_kh, koa_a], 'V')
    plural.add_suffix_rule([koa_e, koa_kh, koa_a], 'C')
    koa_language.add_word_form(plural)
    koa_language.apply_sound_change(SoundChangeRule(koa_h, koa_glottalstop, '_#'))
    koa_language.apply_sound_change(SoundChangeRule([koa_t, koa_i, koa_j], koa_tj, '_V'))
    koa_language.apply_sound_change(SoundChangeRule([koa_t, koa_e, koa_j], koa_tj, '_V'))
    koa_language.apply_sound_change(SoundChangeRule([koa_t, koa_a, koa_j], koa_tj, '_V'))
    koa_language.apply_sound_change(SoundChangeRule([koa_tejective, koa_i, koa_j], koa_tjejective, '_V'))
    koa_language.apply_sound_change(SoundChangeRule([koa_tejective, koa_e, koa_j], koa_tjejective, '_V'))
    koa_language.apply_sound_change(SoundChangeRule([koa_tejective, koa_a, koa_j], koa_tjejective, '_V'))
    genitive = WordFormRule('Genitive', 'N')
    genitive.add_suffix_rule([koa_tejective, koa_a])
    koa_language.add_word_form(genitive)
    genitive_plural = WordFormRule('Genitive Plural', 'N')  # base forms: ['Plural']
    genitive_plural.add_suffix_rule([koa_tejective, koa_a])
    koa_language.add_word_form(genitive_plural)
    inalienable_genitive = WordFormRule('Inalienable Genitive', 'N')  # base forms: ['Genitive']
    inalienable_genitive.add_suffix_rule([koa_c])
    koa_language.add_word_form(inalienable_genitive)
    inalienable_genitive_plural = WordFormRule('Inalienable Genitive Plural', 'N')  # base forms: ['Genitive', 'Plural']
    inalienable_genitive_plural.add_suffix_rule([koa_c])
    koa_language.add_word_form(inalienable_genitive_plural)
    koa_language.apply_sound_change(SoundChangeRule(koa_m, koa_n, '_#'))
    koa_language.apply_sound_change(SoundChangeRule(koa_h, koa_kh))
    koa_language.apply_sound_change(SoundChangeRule(koa_u, None, 'W_C'))
    koa_language.apply_sound_change(SoundChangeRule(koa_y, koa_j))
    koa_language.apply_sound_change(SoundChangeRule(koa_c, koa_ch, '_#'))
    koa_language.apply_sound_change(SoundChangeRule(koa_cejective, koa_chejective, '_#'))
    koa_language.apply_sound_change(SoundChangeRule(koa_r, koa_n, '_C'))
    infinitive = WordFormRule('Infinitive', 'V')
    infinitive.add_prefix_rule([koa_a, koa_s])
    koa_language.add_word_form(infinitive)
    absolutive_antipassive = WordFormRule('Absolutive Antipassive', 'V')
    absolutive_antipassive.add_prefix_rule([koa_u, koa_b])
    koa_language.add_word_form(absolutive_antipassive)
    verbal_antipassive = WordFormRule('Verbal Antipassive', 'V')
    verbal_antipassive.add_prefix_rule([koa_c, koa_u])
    koa_language.add_word_form(verbal_antipassive)
    perfective = WordFormRule('Perfective', 'V')
    perfective.add_suffix_rule([koa_n, koa_i])
    koa_language.add_word_form(perfective)
    progressive = WordFormRule('Progressive', 'V')
    progressive.add_suffix_rule([koa_p, koa_a, koa_t])
    koa_language.add_word_form(progressive)
    imperative = WordFormRule('Imperative', 'V')
    imperative.add_suffix_rule([koa_b, koa_a, koa_l])
    koa_language.add_word_form(imperative)
    optative = WordFormRule('Optative', 'V')
    optative.add_suffix_rule([koa_e, koa_x], 'C')
    optative.add_suffix_rule([koa_x], 'V')
    koa_language.add_word_form(optative)
    negative = WordFormRule('Negative', 'V')
    negative.add_suffix_rule([koa_m, koa_u])
    koa_language.add_word_form(negative)
    irrealis = WordFormRule('Irrealis', 'V')
    irrealis.add_suffix_rule([koa_glottalstop, koa_o], 'V')
    irrealis.add_suffix_rule([koa_o], 'C')
    koa_language.add_word_form(irrealis)
    koa_language.apply_sound_change(SoundChangeRule(koa_n, koa_ng, '_u'))
    koa_language.apply_sound_change(SoundChangeRule([koa_n, koa_m], koa_ng))
    koa_language.apply_sound_change(SoundChangeRule(koa_u, koa_o))

    return koa_language


def add_generated_words(language):
    nouns = language.generate_words(5, 1, 2, 'N', language_stage=0)
    language.add_words(nouns, 0)
    for noun in nouns:
        db.insert_word(noun, language.language_id)
    verbs = language.generate_words(5, 1, 2, 'V', language_stage=0)
    language.add_words(verbs, 0)
    for verb in verbs:
        db.insert_word(verb, language.language_id)


if not db.check_language_by_name("Ko'a"):
    koa_language = generate_koa()
    db.insert_language(koa_language)
    add_generated_words(koa_language)
    print('-'*32)
    koa_language.print_all_word_forms(include_ipa=True, include_base_stem=True)
else:
    koa_language = db.fetch_language_by_name("Ko'a")
    print('-'*32)
    koa_language.print_all_word_forms(include_ipa=True, include_base_stem=True)
