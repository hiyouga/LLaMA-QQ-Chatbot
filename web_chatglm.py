import sys
import json
import logging
from datetime import datetime
from flask import Flask, request
from transformers import AutoTokenizer, AutoModel


logname = '{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')[2:])
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(logname, mode='a', encoding='utf-8'))


class ChatBot:

    def __init__(self, preset='assistant'):
        self._length = 0
        self._prompt_list = json.load(open('prompts.json', 'r', encoding='utf-8'))
        self._preset = preset
        self._history = list()
        self._forget = list()
        self._custom_prompt = tuple()
        self._tokenizer, self._model = self._init_model()
        self.reset()

    def __len__(self):
        return self._length

    @property
    def _prompt(self):
        if self._preset == 'custom':
            return self._custom_prompt
        else:
            prompt = self._prompt_list[self._preset]
            return (eval(prompt['ques']), eval(prompt['resp']))

    def reset(self):
        self._history = [self._prompt]
        self._forget = [True]
        self._length = self.tuple_length(self._prompt)
        logger.info('memory cleared')
        logger.info('prompt: {} {}'.format(self._prompt[0], self._prompt[1]))
        return 0

    def use_preset(self, preset):
        if preset not in self._prompt_list:
            logger.warning('unknown preset')
            return -1
        else:
            self._preset = preset
            self.reset()
            logger.info('preset applied')
            return 0

    def new_prompt(self, prompt):
        if len(prompt) > 500:
            logger.warning('overlength prompt')
            return -1
        response, _ = self._model.chat(self._tokenizer, prompt, history=[])
        self._preset = 'custom'
        self._custom_prompt = (prompt, response)
        self.reset()
        logger.info('new prompt applied')
        return response

    def chat(self, query):
        while self._length + len(query) > 2000: # avoid overlength tokens
            garbage = self._history.pop(0)
            is_forget = self._forget.pop(0)
            self._length -= self.tuple_length(garbage)
            if is_forget:
                self._history.append(self._prompt)
                self._forget.append(True)
                self._length += self.tuple_length(self._history[-1])
                logger.info('emphasize prompt finished')
        response, _ = self._model.chat(self._tokenizer, query, history=self._history)
        if ('抱歉' in response) or ('对不起' in response):
            logger.info('delete this memory')
        else:
            self._history.append((query, response))
            self._forget.append(False)
            self._length += self.tuple_length(self._history[-1])
        return response

    @staticmethod
    def _init_model():
        commit_hash = '4de8efebc837788ffbfc0a15663de8553da362a2'
        tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True, revision=commit_hash)
        model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True, revision=commit_hash).half().cuda()
        model.eval()
        return tokenizer, model

    @staticmethod
    def tuple_length(tup):
        return len(tup[0] + tup[1])

app = Flask(__name__)
bot = ChatBot()

@app.route('/')
def hello():
    logger.info('received GET request')
    return 'I am online'

@app.route('/msg', methods=['POST'])
def msg():
    query = request.form['msg'].strip()
    logger.info('query: {}'.format(query))
    if len(query) > 1500:
        logger.warning('overlength input')
        return '[输入太长了]'
    if query.startswith('/preset'):
        preset = query.replace('/preset', '').strip()
        status = bot.use_preset(preset)
        if status == -1:
            return '[未知的预设]'
        return '[预设已调整为{}]'.format(preset)
    if query.startswith('/prompt'):
        prompt = query.replace('/prompt', '').strip()
        status = bot.new_prompt(prompt)
        if status == -1:
            return '[咒语太长了]'
        return '[咒语吟唱成功]' + status
    if query == '/clear':
        bot.reset()
        return '[记忆重置完成]'
    response = bot.chat(query)
    logger.info('response: {}'.format(response))
    logger.info('token length: {:d}'.format(len(bot)))
    return response

if __name__ == '__main__':
    app.run()
