#from plpr_parser.scraper import *
import glob
import os
import json
import classifier

DATA_PATH = os.environ.get('DATA_PATH', 'data')
TXT_DIR = os.path.join(DATA_PATH, 'txt')
OUT_DIR = os.path.join(DATA_PATH, 'out')
clf = classifier.Classifier(train=False)

def get_party_predictions():
    pred_init = {'leftright':{},'manifestocode':{}}
    pred = {'gruene':pred_init,'cducsu':pred_init,'spd':pred_init,'fdp':pred_init,'linke':pred_init}
    for f in glob.glob(OUT_DIR+'/*-with-classification.json'):
        speeches = json.load(open(f))
        for speech in speeches:
            if speech['speaker_party'] is not None and speech['speaker_party'] in pred.keys():
                for prediction_type in pred_init.keys():
                    for pr in speech['predictions'][prediction_type]:
                        k = pr['label']
                        if not pred[speech['speaker_party']][prediction_type].has_key(k): 
                            pred[speech['speaker_party']][prediction_type][k] = [pr['prediction']]
                        else:
                            pred[speech['speaker_party']][prediction_type][k].append(pr['prediction'])
                            pdb.set_trace()
    json.dump(pred,open(OUT_DIR+'/predictions.json','wb'))
    

def classify_all_speeches():
    for f in glob.glob(OUT_DIR+'/*.json'):
        classify_speeches(f)

def classify_speeches(f):
    data = json.load(open(f))
    data = [v for v in data if v['type'] == 'speech']
    for speech in data:
        speech['predictions'] = clf.predict(speech['text'])
    json.dump(data,open(f.replace('.json','-with-classification.json'),'wb'))

def get_all_bundestags_data():
    fetch_protokolle()
    for filename in os.listdir(TXT_DIR):
        parse_transcript_json(os.path.join(TXT_DIR, filename))

def parse_transcript_json(filename):

    wp, session = file_metadata(filename)
    with open(filename, 'rb') as fh:
        text = clean_text(fh.read())

    data = []

    base_data = {
        'filename': filename,
        'sitzung': session,
        'wahlperiode': wp
    }
    print "Loading transcript: %s/%.3d, from %s" % (wp, session, filename)
    seq = 0
    parser = SpeechParser(text.split('\n'))

    for contrib in parser:
        contrib.update(base_data)
        contrib['sequence'] = seq
        contrib['speaker_cleaned'] = clean_name(contrib['speaker'])
        contrib['speaker_fp'] = fingerprint(contrib['speaker_cleaned'])
        contrib['speaker_party'] = search_party_names(contrib['speaker'])
        seq += 1
        data.insert(0,contrib)

    jsonfile = os.path.basename(filename).replace('.txt', '.json')
    json.dump(data,open(os.path.join(OUT_DIR,jsonfile),'wb'))

 