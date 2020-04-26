from conllu import parse
from pymorphy2 import MorphAnalyzer
pymorphy2_analyzer = MorphAnalyzer()

def read_conllu(conllu_fname): # reading conllu file with parsed sentences
    with open(conllu_fname, 'r', encoding = "UTF-8") as f:
        parsed_sents = f.read()
        sents = parse(parsed_sents)
        return sents

def check_object(token, object_form): # checking if form of object is
                                                    # identical with the form we search for this construction
    if not token['feats']:
        return False
    else:
        if 'Foreign' in token['feats'] and token['feats']['Foreign'] == 'Yes':
            return False
        # print(object_form)
        for feature in object_form:
            if token['feats'][feature] != object_form[feature]:
                return False
        return True


def find_triplet_in_sentence(sent, verb_lemmas, object_form, prep_in_var_of_constr=None, prep_in_constr=None):
                                                        # finding triplet (verb_lemmas, object, prep_in_var_of_constr) for one sentence
    # TODO: подумать про случаи, когда несколько подходящих глаголов в предложении
    syntagrus_pymorphy_dict = {'Acc': 'accs', 'Dat': 'datv', 'Gen': 'gent', 'Ins': 'ablt', 'Loc': 'loct'}

    triplet = {}
    verb_id = None
    object_id = None
    for token in sent:

        # ищем id глагола, чтобы потом искать его зависимые
        if token['lemma'] in verb_lemmas:
            verb_id = token['id']
            triplet['verb'] = token['form']
            triplet['verb_id_for_sent'] = verb_id - 1

        # ищем зависимые (NB: в нашем случае зависимые всегда идут после глагола, поэтому в одном цикле)
        if token['head'] == verb_id:
            pymorphy_object_form = syntagrus_pymorphy_dict[object_form['Case']]
            pymorphy_token = pymorphy2_analyzer.parse(token['form'])
            # ..... # парсинг pymorphy
            # if (token['upostag'] in ['NOUN', 'PROPN', 'PRON'] and check_object(token, object_form)):
            if token['upostag'] in ['NOUN', 'PROPN', 'PRON'] and (check_object(token, object_form) or pymorphy_token[0].tag.case == pymorphy_object_form):
                object_id = token['id']
                break  # мы нашли объект (TODO: bla bla)

    if prep_in_constr and object_id:  # looking for a preposition, if there is
        if prep_in_var_of_constr:
            for token in sent:
                if token['head'] == object_id and token['form'] == prep_in_var_of_constr:
                    triplet['object'] = sent[object_id - 1]['form']
                    triplet['object_id_for_sent'] = object_id - 1
                    triplet['preposition'] = prep_in_var_of_constr
        else:
            for token in sent:  # looking for a preposition, if there isn't
                if token['head'] == object_id:
                    if token['form'] == prep_in_constr:
                        break
                    elif token['upostag']:
                        if token['upostag'] == 'ADP':
                            break

            else:
                triplet['object'] = sent[object_id - 1]['form']
                triplet['object_id_for_sent'] = object_id - 1
    else:
        if object_id:
            triplet['object'] = sent[object_id - 1]['form']
            triplet['object_id_for_sent'] = object_id - 1
    return triplet


def get_all_triples(sentences, verb_lemmas, object_form, prep_in_var_of_constr=None, prep_in_constr=None):
                                                            # finding triplet for all sentences (returns dictionary)
    triples = []
    for i, sent in enumerate(sentences):
        triplet = find_triplet_in_sentence(sent, verb_lemmas, object_form, prep_in_var_of_constr, prep_in_constr)
        triplet['id'] = i
        triples.append(triplet)
    return triples

# def count_triplets(triplets, sentences):
#     count = 0
#     for tr in triplets:
#         if 'object' in tr:
#             count+=1
#             sent_id = tr['id']
#             start_position = tr['verb_id_for_sent']-3
#             if start_position < 0:
#                 start_position = 0
#             end_position = tr['object_id_for_sent']+4
#             if len(sentences[sent_id]) < end_position:
#                 end_position = len(sentences[sent_id])
#
#             tokens = sentences[sent_id][start_position:end_position]
#             preview_list = [token['form'] for token in tokens]
#             print('id', sent_id, *preview_list)
#     return count

def count_necessary_triplets(necessary_triplets, sentences):
    count = len(necessary_triplets)
    for tr in necessary_triplets:
        sent_id = tr['id']

        start_position = tr['verb_id_for_sent']
        end_position = tr['object_id_for_sent']+1
        if len(sentences[sent_id]) < end_position:
            end_position = len(sentences[sent_id])
        # start_position = tr['verb_id_for_sent']-3
        # if start_position < 0:
        #     start_position = 0
        # end_position = tr['object_id_for_sent']+4
        # if len(sentences[sent_id]) < end_position:
        #     end_position = len(sentences[sent_id])

        tokens = sentences[sent_id][start_position:end_position]
        preview_list = [token['form'] for token in tokens]
        print('id', sent_id, *preview_list)

    return count

def show_preview_for_sent(triplet, sentence):
    start_position = triplet['verb_id_for_sent']-3
    if start_position < 0:
        start_position = 0
    end_position = triplet['object_id_for_sent']+4
    if len(sentence) < end_position:
        end_position = len(sentence)
    tokens = sentence[start_position:end_position]
    preview_list = [token['form'] for token in tokens]
    print(*preview_list)

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

    sentences = read_conllu('parsed_sents_ugrozhat_test_2-19.conllu')

    object_form = {'Case': 'Acc'}
    verb_lemmas = ['угрожать']
    prep_in_var_of_constr = None
    prep_in_constr = None

    triplets = get_all_triples(sentences, verb_lemmas, object_form, prep_in_var_of_constr, prep_in_constr)

#    ids = get_indexes(triplets2)
#     print(ids)

    # for tr in triplets:
    #     print(tr)
 #   a = get_standart_date('1456-1876')
#    print(a)


    # print(count_triplets(triplets, sentences))

    print(sentences[370])
    print(sentences[223])

    tokens = sentences[225][0:5]
    preview_list = [token['form'] for token in tokens]
    print(*preview_list)








    # print(find_triplet_in_sentence(sentences1[83], verb_lemmas, object_form, prep_in_var_of_constr=None, prep_in_constr=None))