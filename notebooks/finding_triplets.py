from conllu import parse


def read_conllu(conllu_fname):
    with open(conllu_fname, 'r', encoding = "UTF-8") as f:
        parsed_sents = f.read()
        sents = parse(parsed_sents)
        return sents


def check_object(token, object_form):
    if 'Foreign' in token['feats'] and token['feats']['Foreign'] == 'Yes':
        return False

    # print(object_form)
    for feature in object_form:
        if token['feats'][feature] != object_form[feature]:
            return False
    return True


def find_triplet_in_sentence(sent, verb, object_form, preposition=None, if_preposition=None):
    # TODO: подумать про случаи, когда несколько подходящих глаголов в предложении
    triplet = {}
    verb_id = None
    object_id = None
    for token in sent:

        # ищем id глагола, чтобы потом искать его зависимые
        if token['lemma'] == verb:
            verb_id = token['id']
            triplet['verb'] = token['form']

        # ищем зависимые (NB: в нашем случае зависимые всегда идут после глагола, поэтому в одном цикле)
        if token['head'] == verb_id:
            if token['upostag'] in ['NOUN', 'PROPN', 'PRON'] and check_object(token, object_form):
                object_id = token['id']
                print(token['form'])
                break  # мы нашли объект (TODO: bla bla)

    if preposition and object_id:  # looking for a preposition, if there is
        if if_preposition:
            for token in sent:
                if token['head'] == object_id and token['form'] == preposition:
                    triplet['object'] = sent[object_id - 1]['form']
                    triplet['preposition'] = preposition
        else:
            for token in sent:  # looking for a preposition, if there isn't
                if token['head'] == object_id and token['form'] == preposition:
                    break
            else:
                triplet['object'] = sent[object_id - 1]['form']
    return triplet


def get_all_triples(sentences, verb, object_form, preposition=None, if_preposition=None):
    triples = []
    for i, sent in enumerate(sentences):
        triplet = find_triplet_in_sentence(sent, verb, object_form, preposition, if_preposition)
        triplet['id'] = i
        triples.append(triplet)
    return triples


if __name__ == '__main__':
    sentences = read_conllu('parsed_sents_pisat_k_Dat.conllu')
    object_form = {'Case': 'Dat'} #, 'Animacy': 'Anim'}
    verb = 'писать'
    preposition = 'к'
    if_preposition = True
    sent = sentences[527]
    print(sent)
    print(sent[5])
    triplet = find_triplet_in_sentence(sent, verb, object_form, preposition, if_preposition)
    print(triplet)