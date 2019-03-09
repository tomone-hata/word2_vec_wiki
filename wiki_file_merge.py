import glob
import MeCab
from bs4 import BeautifulSoup
import copy
import pandas as pd
import neologdn
from datetime import datetime

WIKI_FILE_LIST = 'extract/*/*'
WIKI_TEXT = 'output/wiki_text.txt'
WIKI_TEXT_COLUMN = ('title', 'text', 'words', 'basic_words')
#python WikiExtractor.py jawiki-latest-pages-articles\(1\).xml.bz2  -o extract



m = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
def text_to_words(text):
    m.parse('')
    #neologdnにより正規化処理をする。
    text = neologdn.normalize(text)
    m_text = m.parse(text)
    words, basic_words = [], []
    #mecabの出力結果を単語ごとにリスト化
    m_text = m_text.split('\n')
    for row in m_text:
        #Tab区切りで形態素、その品詞等の内容と分かれているので単語部のみ取得
        word = row.split("\t")[0]
        #最終行はEOS
        if word == 'EOS':
            break
        else:
            pos = row.split('\t')[1]
            slice = pos.split(',')
            #品詞を取得する
            parts = slice[0]
            if parts == '記号':
                if word != '。':
                    continue

                #読点のみ残す
                basic_words.append(word)
                words.append(word)
            #活用語の場合は活用指定ない原型を取得する。
            elif slice[0] in ['形容詞', '動詞', '形容動詞', '助動詞']:
                #basic_wordsは付属語は対象外とする。
                if slice[0] != '助動詞':
                    basic_words.append(slice[-3])

                words.append(slice[-3])
            #活用しない語についてはそのままの語を取得する
            else:
                #basic_wordsは名詞のみを対象とする。
                if slice[0] == '名詞':
                    basic_words.append(word)

                words.append(word)

    words = ' '.join(words)
    basic_words = ' '.join(basic_words)
    return words, basic_words


if __name__ == '__main__':
    #引数にとったパスに合致するファイルをリストとして取得する。
    file_list = glob.glob(WIKI_FILE_LIST)
    wiki_list = []
    cnt = 0
    progress = 0
    len_f = len(file_list)
    print('Start to merge wiki files.')
    for i, file in enumerate(file_list):
        cnt = i * 100 // len_f
        with open(file, 'r') as r:
            sentence = ''
            for line in r:
                if '<doc' in line:
                    soup = BeautifulSoup(line, 'lxml')
                    #docタグを取得する。
                    title = soup.doc
                    #docタグからtitleの要素を取得する。
                    title = title.get('title').strip()
                    next(r)
                    next(r)
                elif '</doc>' in line:
                    words, basic_words = text_to_words(sentence)
                    wiki_list.append(copy.copy([title, sentence, words, basic_words]))
                    sentence = ''
                else:
                    sentence += line.strip()

            if cnt > progress:
                now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                print(now ,'%i percent done...' % (cnt))
                progress = cnt
    print('End to merge wiki files.')
    print('Output merge file.')
    df = pd.DataFrame(wiki_list)
    df.to_csv(WIKI_TEXT, sep='\t', index=False, header=WIKI_TEXT_COLUMN)
    print('Finished !!')

'''
彼はとてもかっこいい顔をしているが、 不謹慎な発言が多い。
彼	名詞,代名詞,一般,*,*,*,彼,カレ,カレ
は	助詞,係助詞,*,*,*,*,は,ハ,ワ
とても	副詞,助詞類接続,*,*,*,*,とても,トテモ,トテモ
かっこいい	形容詞,自立,*,*,不変化型,基本形,かっこいい,カッコイイ,カッコイイ
顔	名詞,一般,*,*,*,*,顔,カオ,カオ
を	助詞,格助詞,一般,*,*,*,を,ヲ,ヲ
し	動詞,自立,*,*,サ変・スル,連用形,する,シ,シ
て	助詞,接続助詞,*,*,*,*,て,テ,テ
いる	動詞,非自立,*,*,一段,基本形,いる,イル,イル
不謹慎	名詞,形容動詞語幹,*,*,*,*,不謹慎,フキンシン,フキンシン
な	助動詞,*,*,*,特殊・ダ,体言接続,だ,ナ,ナ
発言	名詞,サ変接続,*,*,*,*,発言,ハツゲン,ハツゲン
が	助詞,格助詞,一般,*,*,*,が,ガ,ガ
多い	形容詞,自立,*,*,形容詞・アウオ段,基本形,多い,オオイ,オーイ
。	記号,句点,*,*,*,*,。,。,。
EOS

'''
