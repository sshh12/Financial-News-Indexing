import gpt_2_simple as gpt2
import numpy as np
import pickle
import tqdm
import os


COMBINE = 50000
MAX_EPOCHS = 100000
RUN = 'run1'
MODEL = '345M'
NEWS_CONTENT_FN = 'dump/news-content-only.pkl'
TRAIN_DATA_FN = 'dump/news-gpt2.npz'


def process_data():

    with open(NEWS_CONTENT_FN, 'rb') as f:
        data = pickle.load(f)

    model_path = os.path.join('models', MODEL)
    enc = gpt2.encoder.get_encoder(model_path)
    raw_text = ''
    token_chunks = []

    for article in tqdm.tqdm(data):
        text = '<|startoftext|>|| {} ||\n\n\n{}<|endoftext|>\n'.format(article[0], article[1])
        raw_text += text
        if len(raw_text) >= COMBINE:
            tokens = np.stack(enc.encode(raw_text))
            token_chunks.append(tokens)
            raw_text = ''
    
    if raw_text:
        tokens = np.stack(enc.encode(raw_text))
        token_chunks.append(tokens)
    
    np.savez_compressed(TRAIN_DATA_FN, *token_chunks)


def train_model():
    # gpt2.download_gpt2(model_name=MODEL)
    sess = gpt2.start_tf_sess()
    gpt2.finetune(sess, TRAIN_DATA_FN, model_name=MODEL, steps=MAX_EPOCHS, run_name=RUN)


if __name__ == '__main__':
    process_data()