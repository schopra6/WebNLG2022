# Preparation of French Corpus
French Corpus is a translated version of WebNLG release3.0 English dataset. We used English to French [NMT model](https://storage.googleapis.com/samanantar-public/V0.3/models/en-indic.zip)  provided by  https://github.com/AI4Bharat/indicTrans to generate hindi sentences. 
## To generate the french corpus
### download the required packages
`pip install -r requirements.txt`
### Generate files for  train,dev and test folder
`python3 run.py <path to the folder containing english xml files>`

In our case, we used english language datapath as it is easy to replace english lex with french lex. WebNLG corpus can be downloaded from [this repository](https://gitlab.com/shimorina/webnlg-dataset).
