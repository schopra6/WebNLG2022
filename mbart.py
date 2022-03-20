

import json




import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast, Seq2SeqTrainingArguments, Seq2SeqTrainer,EarlyStoppingCallback

from datasets import load_metric

import numpy as np

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--model_name", type=str, default='mbart-large-50')#, required=True)
#parser.add_argument("--train_file", type=str, default=None)#, required=True)
#parser.add_argument("--eval_file", type=str, default=None)#, required=True)
parser.add_argument("--lr", type=float, default=1e-6)
parser.add_argument("--batch_size", type=int, default=1)
parser.add_argument("--epochs", type=int, default=3)
parser.add_argument("--checkpoint_dir", type=str, default=None)
parser.add_argument("--checkpoint_name", type=str, default=None)
parser.add_argument("--tokenizer_dir", type=str, default=None)
parser.add_argument("--save_dir", type=str, default='models/')
parser.add_argument("--log_dir", type=str, default='logs/')
parser.add_argument("--task", type=str, default='nmt')
parser.add_argument("--label_smoothing_factor", type=float, default=0)
parser.add_argument("--warmup_steps", type=int, default=600)

args = parser.parse_args("")



"""Template for MLM pretraining of mBART"""

# Imports


# SetUp Tokenizer
def add_special_tokens(tokenizer, codes, languageccumulation_steps_codes=True):
    special_tokens_dict = {'additional_special_tokens':[]}
    for code in codes:
        special_tokens_dict['additional_special_tokens'].append(code)
    tokenizer.add_special_tokens(special_tokens_dict)
    if language_codes:
        for code in codes:
            tokenizer.lang_code_to_id[code] = tokenizer.convert_tokens_to_ids(code)

if args.checkpoint_dir is None:
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50")
    tokenizer.build_inputs_with_special_tokens(['[sj]', '[p]', '[o]', '[t]'])
    #add_special_tokens(tokenizer, ['en_XX'])
    #add_special_tokens(tokenizer, ['[sj]', '[p]', '[o]', '[t]'], False)
    #tokenizer=tokenizer.save_pretrained(args.save_dir+args.model_name)
else:
    #tokenizer = MBartTokenizer.from_pretrained(args.checkpoint_dir)
    tokenizer =  MBart50TokenizerFast.from_pretrained(args.tokenizer_dir)#AutoTokenizer.from_pretrained(args.tokenizer_dir)
        
# SetUp Model
if args.checkpoint_name is None:
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50")
    model.resize_token_embeddings(len(tokenizer))
else:
    model = MBartForConditionalGeneration.from_pretrained(args.checkpoint_dir + args.checkpoint_name)

# SetUp Collators
def mlm_collator(features:list):
    # Parse Data
    inputs = [f['mlm']['text'] for f in features]
    labels = [f['mlm']['text'] for f in features]
    langs = [f['mlm']['lang'] for f in features]
    
    # Encode languages
    # langs = tokenizer(langs, max_length=128, padding=True, truncation=True, add_special_tokens=False, return_tensors='pt').input_ids
    
    # Encode inputs
    inputs = tokenizer(inputs, max_length=128, padding=True, truncation=True, add_special_tokens=True, return_tensors='pt').input_ids
    inputs[inputs==tokenizer.convert_tokens_to_ids(tokenizer.src_lang)] = langs.reshape(-1)
    special_tokens_mask = [
        tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in inputs.tolist()
    ]
    probability_matrix = torch.full(inputs.shape, 0.35)
    probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool), value=0.0)
    padding_mask = inputs.eq(tokenizer.pad_token_id)
    probability_matrix.masked_fill_(padding_mask, value=0.0)
    masked_indices = torch.poisson(probability_matrix).bool()
    inputs[masked_indices] = tokenizer.convert_tokens_to_ids(tokenizer.mask_token)
    
    # Inputs attention mask
    attention_mask = (~masked_indices).float()
    attention_padding_mask = inputs.eq(tokenizer.pad_token_id)
    attention_mask.masked_fill_(attention_padding_mask, value=1.0)
    
    # Encode labels
    labels = tokenizer(labels, max_length=128, padding=True, truncation=True, add_special_tokens=True, return_tensors='pt').input_ids
    labels[labels==tokenizer.convert_tokens_to_ids(tokenizer.src_lang)] = langs
    labels_padding_mask = labels.eq(tokenizer.pad_token_id)
    labels[labels_padding_mask] = -100
    
    batch = {
        'input_ids': inputs,
        'attention_mask': attention_mask,
        'labels': labels
    }

    return batch

def setup(split):
        #for split in ('train', 'dev', 'test'):
            with open(f"data/{split}/linearized_rdf_input.json") as f:
                texts_mapping = json.load(f)

            with open(f"data/{split}/texts_output.json") as f:
                decoder_texts_mapping = json.load(f)

            assert set(texts_mapping.keys()) == set(decoder_texts_mapping.keys())

            keys = list(texts_mapping.keys())
            texts = [texts_mapping[key] for key in keys]
            texts = [x.replace("<s>", "<sj>") for x in texts]
            decoder_texts = [decoder_texts_mapping[key] for key in keys]
            objects = [
                {'nmt':{'src':  text, 'tgt': decoder_text,'src_lang': 'en_XX','trg_lang':'en_XX'}} for text, decoder_text in zip(texts, decoder_texts)
            ]
            return objects

def nmt_collator(features:list):
    # Parse Data
    inputs = [f['nmt']['src'] for f in features]
    tgt_text = [f['nmt']['tgt'] for f in features]
    src_langs = [f['nmt']['src_lang'] for f in features]
    trg_langs = [f['nmt']['trg_lang'] for f in features]
    tokenizer.src_lang = src_langs[0]
    tokenizer.tgt_lang = trg_langs[0]
    # Encode languages
    #src_langs = tokenizer(src_langs, max_length=128, padding=True, truncation=True, add_special_tokens=False, return_tensors='pt').input_ids
    #trg_langs = tokenizer(trg_langs, max_length=128, padding=True, truncation=True, add_special_tokens=False, return_tensors='pt').input_ids

    # encode X and Y together to ensure equal padding
    seqs = inputs #+ labels
    seqs = tokenizer(seqs, max_length=128, padding=True, truncation=True, add_special_tokens=True, return_tensors='pt')
    
    # Encode inputs
    input_mask = seqs.attention_mask
    input_ids = seqs.input_ids
    #input_ids[input_ids==tokenizer.convert_tokens_to_ids(tokenizer.src_lang)] = src_langs.reshape(-1)
    
    # Encode labels
    labels=[]
    with tokenizer.as_target_tokenizer():
         labels = tokenizer(tgt_text,max_length=128, padding=True, truncation=True, add_special_tokens=True, return_tensors="pt")
    labels = labels.input_ids
    #labels[labels==tokenizer.convert_tokens_to_ids(tokenizer.src_lang)] = trg_langs.reshape(-1)
    labels_padding_mask = labels.eq(tokenizer.pad_token_id)
    labels[labels_padding_mask] = -100
    
    batch = {
        'input_ids': input_ids,
        'attention_mask': input_mask,
        'labels': labels
    }

    return batch

if args.task == 'mlm':
    collator = mlm_collator
elif args.task == 'nmt':
    collator = nmt_collator

#tokenizer=MBartTokenizer.from_pretrained('facebook/mbart-large-cc25',src_lang="en_XX")

train_dataset = setup('train')#json.load(open(args.train_file, "r"))
eval_dataset = setup('dev')#json.load(open(args.eval_file, "r"))

# SetUP Metrics

bleu = load_metric('sacrebleu')

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits[0], axis=-1)
    labels[labels==-100] = 1
    labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    labels = [[l] for l in labels]
    predictions = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    bleu_score = bleu.compute(predictions=predictions, references=labels)['score']
    return {'BLEU': bleu_score}

# SetUp Training
train_args = Seq2SeqTrainingArguments(
    output_dir=args.save_dir+args.model_name,
    do_train=True,
    do_eval=True,
    evaluation_strategy ='steps',
    eval_steps = 500,
    save_steps = 500,
    logging_steps = 500,
    save_total_limit = 1,
    load_best_model_at_end=True,
    per_device_train_batch_size=args.batch_size,
    per_device_eval_batch_size=args.batch_size,
    learning_rate=args.lr,
    warmup_steps = args.warmup_steps,
    lr_scheduler_type='linear',
    adam_beta2=0.98,
    label_smoothing_factor=args.label_smoothing_factor,
    num_train_epochs=args.epochs,
    logging_dir=args.log_dir+args.model_name,
    gradient_accumulation_steps=4,
    fp16=True,
    )

trainer = Seq2SeqTrainer(
    model=model, 
    args=train_args, 
    data_collator=collator, 
    train_dataset=train_dataset, 
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
)

# Starting Evaluation
trainer.evaluate()

# Run Training
trainer.train()

