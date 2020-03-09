from conllu import parse

def read_conllu(conllu_fname): # reading conllu file with parsed sentences
    with open(conllu_fname, 'r', encoding = "UTF-8") as f:
        parsed_sents = f.read()
        sents = parse(parsed_sents)
        return sents

def check_object(token, object_form): # checking if form of object is
                                                    # identical with the form we search for this construction
    if 'Foreign' in token['feats'] and token['feats']['Foreign'] == 'Yes':
        return False
    # print(object_form)
    for feature in object_form:
        if token['feats'][feature] != object_form[feature]:
            return False
    return True


def find_triplet_in_sentence(sent, verb, object_form, preposition=None, if_preposition=None):
                                                        # finding triplet (verb, object, preposition) for one sentence
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
                break  # мы нашли объект (TODO: bla bla)

    if if_preposition and object_id:  # looking for a preposition, if there is
        if preposition:
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
                                                            # finding triplet for all sentences (returns dictionary)
    triples = []
    for i, sent in enumerate(sentences):
        triplet = find_triplet_in_sentence(sent, verb, object_form, preposition, if_preposition)
        triplet['id'] = i
        triples.append(triplet)
    return triples

def count_triplets(triplets):
    count = 0
    for tr in triplets:
        if 'object' in tr:
            count+=1
    return count

def get_indexes(triplets):
    ids = []
    for tr in triplets:
        if 'object' in tr:
            ids.append(tr['id'])
    return ids

def get_standart_date(date):
    if date.find('-') != -1:
        date_array = date.split('-')
        mean_date = (int(date_array[0]) + int(date_array[1])) // 2 #если произведение создавалось несколько лет, то берём среднее арифметическое верхней и нижней границы
        return mean_date
    else:
        date_array = date.split('.')
        return date_array[0]

if __name__ == '__main__':
    sentences1 = read_conllu('parsed_sents_pisat_k_Dat.conllu')
    object_form = {'Case': 'Dat'} #, 'Animacy': 'Anim'}
    verb = 'писать'
    preposition = 'к'
    if_preposition = True
    triplets1 = get_all_triples(sentences1, verb, object_form, preposition, if_preposition)

    sentences2 = read_conllu('parsed_sents_pisat_Dat.conllu')
    object_form = {'Case': 'Dat'} #, 'Animacy': 'Anim'}
    verb = 'писать'
    preposition = False
    if_preposition = True
    triplets2 = get_all_triples(sentences2, verb, object_form, preposition, if_preposition)

    ids = get_indexes(triplets2)
#     print(ids)

#     for tr in triplets2:
#         print(tr)
    a = get_standart_date('1456-1876')
    print(a)
