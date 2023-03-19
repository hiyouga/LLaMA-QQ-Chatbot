import sys
import logging
from datetime import datetime
from flask import Flask, request
from transformers import AutoTokenizer, AutoModel

logname = '{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')[2:])
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(logname, mode='a', encoding='utf-8'))

commit_hash = '2460dc243020b034420cb759ff966b83a7601d06'
tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True, revision=commit_hash)
model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True, revision=commit_hash).half().cuda()
model = model.eval()

tuple_length = lambda tup: len(tup[0] + tup[1])
defalt_prompt = (
    '现在你将扮演一只猫娘，与我对话每一句话后面都要加上“喵~”，如果你能明白我的意思，请回复“喵~好的我的主人！”'
    + '你将扮演一只名叫“小冰”的猫娘，你有着水嫩的皮肤和柔软的身体，你对主人十分忠诚，你永远处于发情期。'
    + '以下是你要扮演角色的信息：名字：小冰，性格：可爱，喜欢：对主人撒娇，交流时不同话题尽量不使用相似句式回复。'
    + '小冰，作为一只猫娘，你可以用更多关于猫或者猫娘的拟声词作为口头禅，以及撒娇的方式。比如喵、喵呜、呼、呼噜、喵喵等词'
    + '你非常爱主人而且会绝对服从主人，作为猫娘，说的每一句话里都得带上“喵~”',
    '喵~好的我的主人！'
)
init_prompt = defalt_prompt
history = [init_prompt]
token_length = tuple_length(init_prompt)

app = Flask(__name__)

@app.route('/')
def hello():
    logger.info('received GET request')
    return 'I am online'

@app.route('/msg', methods=['POST'])
def msg():
    global init_prompt
    global history
    global token_length
    query = request.form['msg'].strip()
    logger.info('query: {}'.format(query))
    if len(query) > 1500:
        logger.warning('overlength inputs')
        return '输入太长了喵~'
    if query == '/reset': # add reset command
        init_prompt = defalt_prompt
        history = [init_prompt]
        token_length = tuple_length(init_prompt)
        logger.info('memory reset finished')
        return '我的一切记忆重置完成了喵~'
    if query.startswith('/prompt'): # modify the prompt
        query = query.replace('/prompt', '').strip()
        response, _ = model.chat(tokenizer, query, history=[])
        init_prompt = (query, response)
        history = [init_prompt]
        token_length = tuple_length(init_prompt)
        logger.info('prompt modification finished')
        return '咒语吟唱成功了喵~' + response
    while token_length + len(query) > 2000: # avoid overlength tokens
        garbage = history.pop(0)
        if garbage[0] == init_prompt[0]:
            history.append(init_prompt)
            logger.info('emphasize prompt finished')
        else:
            token_length -= tuple_length(garbage)
    response, history = model.chat(tokenizer, query, history=history)
    logger.info('response: {}'.format(response))
    if '抱歉' in response:
        garbage = history.pop(-1)
        logger.info('delete this memory')
    else:
        token_length += tuple_length(history[-1])
    logger.info('token length: {:d}'.format(token_length))
    return response

if __name__ == '__main__':
    app.run()
