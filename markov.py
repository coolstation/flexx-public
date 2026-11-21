## Markov Chain Core.

## The bulk of the core markov chaining is Micolithe's work. Some
## tweaks have been made, and coolstatino stank rubbed on, by warc.

## On-the-fly markov order setting and checking added by
## SpacingNevada.

import random
import re
import datetime
import helpers

h = helpers.Helpers()

class MarkovChainer():
    def __init__(self, order):
        self.order = order
        self.beginnings = []
        self.freq = {}
        random.seed(datetime.datetime.utcnow().timestamp())

    def set_order(self, order):
        """change the order setting on the fly"""
        h.logger("Order set begins!","Debug")
        if order > 1:
            h.logger("Order > 1, changing!","Debug")
            self.order = order
            h.logger("Order changed!","Debug")
        else:
            h.logger("Order <= 1, fuck off!","Debug")
            raise ValueError("order value must be greater than 1")

    def get_order(self):
        """check the value of order"""
        return self.order

    # pass a string with a terminator to the function to add it to the markov lists.
    def add_sentence(self, string, terminator):
        data = "".join(string)
        words = data.split()
        buf = []
        if len(words) > self.order:
            words.append(terminator)
            self.beginnings.append(words[0:self.order])
        else:
            pass

        for word in words:
            buf.append(word)
            if len(buf) == self.order + 1:
                mykey = (buf[0], buf[-2])
                if mykey in self.freq:
                    self.freq[mykey].append(buf[-1])
                else:
                    self.freq[mykey] = [buf[-1]]
                buf.pop(0)
            else:
                continue

    def add_text(self, text):
        text = re.sub(r'\n\s*\n/m', ".", text)
        seps = '([.!?;:])'
        if not re.search(r'([.!?;:]$)', text):
            text = text + '.'
        pieces = re.split(seps, text)
        sentence = ""
        for piece in pieces:
            if piece != "":

                if re.search(seps, piece):
                    self.add_sentence(sentence, piece)
                    sentence = ""
                else:
                    sentence = piece

    # Generate the goofy sentences that become your tweet.
    def __generate_sentence(self, prompt=""):
        if prompt != "":
            h.logger("Generating sentence, prompt?: " + prompt, "Info")
            seps = '([.!?;:])'
            prompts = []
            data = "".join(prompt)
            words = data.split()
            buf = []
            if len(words) > self.order:
                for word in words:
                    #if re.search(r'flexx', word) is not None:
                    #    continue
                    h.logger(str(word), "word")
                    buf.append(word)
                    if len(buf) == self.order :
                        h.logger(str(buf), "buf")
                        prompts.append(buf[0:self.order])
                        buf.pop(0)
                    else:
                        continue
                if len(prompts) != 0:
                    h.logger(str(prompts), "prompts")
                    res=random.choice(prompts)
                    h.logger("picked a prmpo", "Info")

            else:
                h.logger("prompt too short, resorting to random", "Info")
                res = random.choice(self.beginnings)
                res = res[:]

        else:
            res = random.choice(self.beginnings)
            res = res[:]

        h.logger("res:" + str(res) + " with length " + str(len(res)) , "Info")

        if len(res) == self.order:
            h.logger("len(res) == self.order", "Info")
            nw = True
            while nw is not None:
                restup = (res[-2], res[-1])
                h.logger(str(restup), "restup")
                try:
                    nw = self.next_word_for(restup)
                    if nw is not None:
                        res.append(nw)
                        h.logger("res append", "Info")
                    else:
                        if len(res) <= (self.order +1):
                            filler = random.choice(self.beginnings)
                            nw = "filler"
                            res.append("?")
                            h.logger("bad prompt, added filler", "Info")
                            res.append(filler[-2])
                            res.append(filler[-1])
                        h.logger("no more words", "Info")
                        continue
                except:
                    nw = False



            sentence = ""
            for word in res:
                sentence += word + " "
                h.logger(word, "word in new res")
            h.logger(str(res), "res")
            h.logger(str(res[-2]), "res-2")
            h.logger(str(res[-1]), "res-1")

        else:
            h.logger("None! wow!!  ", "Info")
            sentence = None
        return sentence

    def next_word_for(self, words):
        try:
            arr = self.freq[words]
            next_words = random.choice(arr)
            return next_words
        except:
            return None

    def generate_sentence(self, prompt=""):
        h.logger("wow we called generate_sentence with prompt: " + prompt, "Info")
        keeptrying = True
        while keeptrying:
            # pycharm says __generate_sentence() doesnt return anything which is a bold-faced lie
            txt = self.__generate_sentence(prompt)
            if "…" not in txt:
                keeptrying = False
            else:
                pass
                # play it again sam
                print("found an incomplete sentence. retrying")
                print(txt)
        return txt
