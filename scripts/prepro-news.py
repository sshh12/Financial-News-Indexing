from nltk.tokenize import word_tokenize
import pickle
import ujson
import tqdm
import os


NEWS_DATA_FN = 'dump/news.data'


def pkl(prefix, name, obj):
    with open('{}-{}.pkl'.format(prefix, name), 'wb') as fp:
        pickle.dump(obj, fp)


def main():

    path, ext = os.path.splitext(NEWS_DATA_FN)
    
    objs = []
    all_tokens = set()
    all_sources = set()
    all_days = set()
    with open(NEWS_DATA_FN, 'r', encoding='utf-8') as rf:
        for line in tqdm.tqdm(rf.readlines()):
            obj = ujson.loads(line)['_source']
            obj['len'] = len(obj['content'])
            obj['tokens'] = word_tokenize(obj['content'])
            obj['tokens_set'] = set(obj['tokens'])
            obj['day'] = obj['date'].split('T')[0]
            all_tokens |= obj['tokens_set']
            all_sources.add(obj['source'])
            all_days.add(obj['day'])
            objs.append(obj)

    meta = dict(
        tokens=sorted(all_tokens), 
        sources=sorted(all_sources), 
        days=sorted(all_days)
    )
    pkl(path, 'meta', meta)

    pkl(path, 'all', objs)

    data_by_param = {name: [] for name in sorted(all_sources)}
    [data_by_param[item['source']].append((i, item)) for i, item in enumerate(objs)]
    for name, objs_ in data_by_param.items(): objs_.sort(key=lambda x: x[1]['date'])
    idxs_by_param = {name: [item[0] for item in objs_] for name, objs_ in data_by_param.items()}
    pkl(path, 'by-source', idxs_by_param)

    data_by_param = {name: [] for name in sorted(all_days)}
    [data_by_param[item['day']].append((i, item)) for i, item in enumerate(objs)]
    for name, objs_ in data_by_param.items(): objs_.sort(key=lambda x: x[1]['date'])
    idxs_by_param = {name: [item[0] for item in objs_] for name, objs_ in data_by_param.items()}
    pkl(path, 'by-day', idxs_by_param)

    content_only = [(obj['headline'], obj['content']) for obj in objs]
    content_only.sort(key=lambda x: len(x[1]))
    pkl(path, 'content-only', content_only)


if __name__ == '__main__':
    main()